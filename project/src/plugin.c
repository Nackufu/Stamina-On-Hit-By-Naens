/* Stamina On Hit - By Naens 1.1.0 -- TESV 1.9.32 / SKSE 1.7.3.
 * Uses the physical-hit notification path, NOT a timer to merge hit events.
 * ABI/address provenance: docs/ABI_SOURCES.md.
 */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <shlobj.h>
#include <stdio.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>
#include "MinHook.h"
#include "hit_filter.h"

typedef struct {
    uint32_t skseVersion, runtimeVersion, editorVersion, isEditor;
    void *(__cdecl *QueryInterface)(uint32_t);
    uint32_t (__cdecl *GetPluginHandle)(void);
    uint32_t (__cdecl *GetReleaseIndex)(void);
} SKSEInterface;
typedef struct { uint32_t infoVersion; const char *name; uint32_t version; } PluginInfo;
typedef struct { const char *sender; uint32_t type, dataLen; void *data; } Message;
typedef struct {
    uint32_t interfaceVersion;
    bool (__cdecl *RegisterListener)(uint32_t, const char *, void (__cdecl *)(Message *));
    bool (__cdecl *Dispatch)(uint32_t, uint32_t, void *, uint32_t, const char *);
    void *(__cdecl *GetEventDispatcher)(uint32_t);
} Messaging;
typedef struct {
    void *target, *caster;
    uint32_t source, projectile;
    uint8_t flags;
    uint8_t padding[3]; /* NEVER read this padding as flags or extended hit data. */
} HitEvent;
typedef struct { const char *data; } FixedString;
typedef struct { FixedString name, arg; float number; void *sender; } ModEvent;
typedef struct Context {
    void *target, *caster;
    uint32_t source, projectile;
    bool seen, accepted;
} Context;
typedef void (__thiscall *PhysicalSend)(void *, void **, void **, uint32_t, uint32_t, void *);
typedef void (__thiscall *AddSink)(void *, void *);
typedef void (__thiscall *SendEvent)(void *, void *);
typedef void *(__cdecl *LookupForm)(uint32_t);
typedef void *(__thiscall *StringCtor)(FixedString *, const char *);
typedef void (__thiscall *StringRelease)(FixedString *);

static PhysicalSend original_send;
static void *mod_dispatcher;
static DWORD context_tls = TLS_OUT_OF_INDEXES;
static bool installed;
static bool attempted;
static Messaging *messaging;
static char log_path[MAX_PATH];

_Static_assert(sizeof(void *) == 4, "Oldrim requires x86");
_Static_assert(offsetof(HitEvent, flags) == 0x10, "hit ABI");
_Static_assert(sizeof(ModEvent) == 0x10, "mod callback ABI");
_Static_assert(sizeof(SKSEInterface) == 0x1C, "SKSE ABI");

static void log_line(const char *message) {
    if (!log_path[0]) return;
    FILE *f = fopen(log_path, "a");
    if (f) { fprintf(f, "%s\n", message); fclose(f); }
}
static void init_log(void) {
    char documents[MAX_PATH];
    if (SUCCEEDED(SHGetFolderPathA(NULL, CSIDL_PERSONAL, NULL, SHGFP_TYPE_CURRENT, documents))) {
        snprintf(log_path, sizeof(log_path), "%s\\My Games\\Skyrim\\SKSE\\StaminaOnHitByNaens.log", documents);
        FILE *f = fopen(log_path, "w");
        if (f) { fputs("Stamina On Hit - By Naens 1.1.0\n", f); fclose(f); }
    }
}
static uint8_t form_type(void *p) { return *((uint8_t *)p + 0x12); }

/* An explicit MSVC-compatible two-slot BSTEventSink vtable avoids relying on
 * the MinGW C++ ABI. The singleton lives until process exit; it is never freed. */
static void *__thiscall sink_delete(void *self, unsigned flags) { (void)flags; return self; }
static uint32_t __thiscall receive_hit(void *self, HitEvent *e, void *dispatcher) {
    (void)self; (void)dispatcher;
    Context *c = (Context *)TlsGetValue(context_tls);
    if (!c || c->seen || !e || e->target != c->target || e->caster != c->caster ||
        e->source != c->source || e->projectile != c->projectile) return 0;
    c->seen = true;
    if (!e->caster || form_type(e->caster) != 62 || !e->target || e->target == e->caster) return 0;
    void *source = ((LookupForm)0x00451A30)(e->source);
    if (!source || form_type(source) != 41) return 0;
    c->accepted = nsh_qualifies(true, true, true, form_type(e->target),
                                form_type(source), *((uint8_t *)source + 0xF1),
                                e->projectile, e->flags);
    return 0; /* kEvent_Continue: do not consume the game's or other mods' event. */
}
static void *sink_vtable[2] = { (void *)sink_delete, (void *)receive_hit };
static struct { void **vtable; } sink = { sink_vtable };

static void emit_reward(void *attacker) {
    ModEvent e = {0};
    ((StringCtor)0x00A511C0)(&e.name, "NSH_PhysicalMeleeHit_v2");
    ((StringCtor)0x00A511C0)(&e.arg, "");
    e.number = 0.0f; /* Amount comes from persistent MCM settings. */
    e.sender = attacker;
    ((SendEvent)0x006EBC10)(mod_dispatcher, &e);
    ((StringRelease)0x00A511B0)(&e.arg);
    ((StringRelease)0x00A511B0)(&e.name);
}

/* __fastcall receives ECX=this and consumes EDX; the remaining five arguments
 * exactly match the original __thiscall function's stack arguments. */
static void __fastcall physical_send(void *holder, void *unused_edx, void **target,
                                    void **attacker, uint32_t source, uint32_t projectile,
                                    void *hit_data) {
    (void)unused_edx;
    Context current = {target ? *target : NULL, attacker ? *attacker : NULL,
                       source, projectile, false, false};
    void *previous = TlsGetValue(context_tls);
    if (!TlsSetValue(context_tls, &current)) {
        original_send(holder, target, attacker, source, projectile, hit_data);
        return;
    }
    original_send(holder, target, attacker, source, projectile, hit_data);
    TlsSetValue(context_tls, previous);
    if (current.accepted) emit_reward(current.caster);
}

static void __cdecl on_message(Message *message) {
    if (!message || message->type != 8 || installed || attempted) return; /* DataLoaded */
    attempted = true;
    mod_dispatcher = messaging->GetEventDispatcher(0);
    if (!mod_dispatcher) { log_line("DISABLED: SKSE mod-event dispatcher unavailable."); return; }
    /* Refuse an already-detoured entry rather than overwrite an unknown hook. */
    uint8_t entry = *(uint8_t *)0x006E4060;
    if (entry == 0xE9 || entry == 0xEB || entry == 0xCC) {
        log_line("DISABLED: physical-hit entry already patched; possible plugin conflict."); return;
    }
    context_tls = TlsAlloc();
    if (context_tls == TLS_OUT_OF_INDEXES) { log_line("DISABLED: TLS allocation failed."); return; }
    MH_STATUS status = MH_Initialize();
    if (status == MH_OK) status = MH_CreateHook((void *)0x006E4060, (void *)physical_send, (void **)&original_send);
    if (status != MH_OK) {
        log_line("DISABLED: MinHook could not create the physical-hit trampoline.");
        TlsFree(context_tls); context_tls = TLS_OUT_OF_INDEXES; return;
    }
    ((AddSink)0x006E3E30)((void *)0x012E4F60, &sink);
    status = MH_EnableHook((void *)0x006E4060);
    if (status != MH_OK) {
        log_line("DISABLED: MinHook could not enable the physical-hit trampoline."); return;
    }
    installed = true;
    log_line("ACTIVE: physical-hit hook installed; player + NPC; MCM-controlled amounts; melee types 1-6; bash excluded.");
    log_line("ESP + NSH_PlayerAlias.pex required. SkyUI 5.1 LE supplies the MCM.");
}

__declspec(dllexport) bool __cdecl SKSEPlugin_Query(const SKSEInterface *skse, PluginInfo *info) {
    init_log();
    if (!skse || !info) return false;
    info->infoVersion = 1; info->name = "Stamina On Hit - By Naens"; info->version = 110;
    if (skse->isEditor || skse->runtimeVersion != 0x09200000 ||
        skse->skseVersion != 0x01070030 || (uintptr_t)GetModuleHandleA(NULL) != 0x00400000) {
        log_line("REJECTED: requires TESV 1.9.32.0, SKSE 1.7.3, standard executable image base."); return false;
    }
    return true;
}
__declspec(dllexport) bool __cdecl SKSEPlugin_Load(const SKSEInterface *skse) {
    messaging = (Messaging *)skse->QueryInterface(5);
    if (!messaging || messaging->interfaceVersion < 2) return false;
    bool ok = messaging->RegisterListener(skse->GetPluginHandle(), "SKSE", on_message);
    log_line(ok ? "Loaded; waiting for DataLoaded." : "DISABLED: SKSE listener registration failed.");
    return ok;
}

#ifdef NSH_TEST
/* Test-build exports only; absent from the distributed runtime DLL. */
__declspec(dllexport) void __cdecl NSH_TestSetup(void *original, void *dispatcher) {
    original_send = (PhysicalSend)original;
    mod_dispatcher = dispatcher;
    context_tls = 1;
}
__declspec(dllexport) void __cdecl NSH_TestPhysical(void **target, void **attacker,
                                                   uint32_t source, uint32_t projectile) {
    physical_send((void *)0x012E4C30, NULL, target, attacker, source, projectile, NULL);
}
__declspec(dllexport) void __cdecl NSH_TestEvent(HitEvent *e) {
    receive_hit(&sink, e, (void *)0x012E4F60);
}
#endif

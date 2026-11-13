# Validation — Stamina On Hit - By Naens 1.1.0

Date: 2026-11-13. Target: TESV 1.9.32.0 x86, SKSE 1.7.3, SkyUI 5.1 LE.

## Completed

- Rebuilt the production Windows x86 DLL and a separate test DLL from the checked-in C source with ziglang 0.17.1 / MinHook.
- Compiled both PSC files to big-endian Skyrim PEX 3.2, game ID 1 with papyrus-compiler 2026.03.15. Only the two mod scripts are installed.
- Independently decompiled both PEX files with Champollion; resulting source is included in this directory. The MCM compilation uses inherited property accessors for ModName and Pages.
- C filter tests: 320 weapon-type/flag combinations and six exclusion cases pass.
- Unicorn executes the actual compiled x86 bridge with mocked Win32/engine functions: player and NPC attackers, NPC-to-player hits, melee weapon types 1–6, blocked/power flags, bash/projectile/magic/unarmed/nonactor exclusions, repeated callback suppression, consecutive physical hits, nested calls, TLS context restoration, cdecl/thiscall stack balance and sender payload pass. The emitted v2 event contains the attacker, not the victim; numArg is zero.
- Independent PEX parser and bytecode interpreter execute the supplied binaries with mocked Skyrim/SkyUI APIs: init/load registration, removal of the v1 subscription, player/NPC reward selection, nonactor rejection, independent toggles, default 10, different amounts, zero refund, 0–100 clamp, MCM title/page, slider range/interval, default resets, unknown-option rejection, refresh without resetting settings, and a fresh alias instance reading retained global values all pass. This simulates retained values, not actual Skyrim save serialization.
- ESP parser verifies Form 43, Skyrim.esm master, 4 GLOB + 2 QUST, record/group sizes, SGE/RunOnce flags, forced player aliases, VMAD scripts, both SEQ entries and unchanged controller identity. Neither alias has Essential or Protected flags. There are no vanilla overrides.
- PE inspection confirms x86/PE32, only SKSEPlugin_Query and SKSEPlugin_Load exports in production, and Windows system imports.
- Packager validates XML and installer source paths, the runtime DLL allowlist, archive CRC and every included SHA256 checksum. No test DLL, PDB, import library, SkyUI core PEX or compiler binary is shipped.

## Not performed here

No Skyrim executable or running game is available. The actual detour/trampoline installation, actor lifetimes under gameplay, Papyrus scheduling under load, SkyUI registration/UI rendering, old-save quest startup, real save serialization and interaction with the user's complete mod list have not been tested for 1.1.0. Creation Kit GUI and Bethesda's official Papyrus compiler were not run. The included tests use mocks and cannot certify game stability.

The user reported that 1.0.0-beta.1 worked in game. 1.1.0 retains that bridge design and controller identity, expands the accepted attacker set, and introduces new settings/MCM behavior; it requires its own in-game acceptance test. See TEST_PLANI_TR.md.

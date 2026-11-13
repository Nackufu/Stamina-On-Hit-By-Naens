# ABI and build provenance

Only Skyrim classic/TESV 1.9.32.0 is supported. No SSE/AE addresses were used.

| Item | Primary implementation reference |
|---|---|
| SKSE interface, messaging version 2, DataLoaded=8, dispatcher 0 | SKSE 1.7.3 official source, PluginAPI.h |
| LookupFormByID 0x00451A30 | SKSE 1.7.3 GameForms.cpp |
| Hit dispatcher 0x012E4F60; AddEventSink 0x006E3E30; SendEvent 0x006EBC10 | SKSE 1.7.3 GameEvents.h/.cpp |
| Form type offset 0x12; weapon animation type offset 0xF1 | SKSE 1.7.3 GameForms.h / GameObjects.h |
| FixedString ctor/release 0x00A511C0 / 0x00A511B0 | SKSE 1.7.3 GameTypes.h |
| Mod event layout and string ownership | SKSE 1.7.3 PapyrusEvents.h/.cpp and PapyrusForm.cpp |
| Physical SendHitEvent_B at 0x006E4060, five stack args | DavidJCobb/skyrim-classic-re, ReverseEngineered/Systems/BSTEvent.h |
| Physical attack path sends event before damage/block processing | Same repository, ReverseEngineered/_DOCS/Actor/ProcessIncomingAttack.h |
| Hit flags are one byte at offset 0x10 (do not interpret padding) | Same repository, ReverseEngineered/Systems/BSTEvent.h |
| ESP/QUST/alias VMAD format | TES5Edit/TES5Edit Core/wbDefinitionsTES5.pas |
| PEX 3.2 format/opcodes | Orvid/Caprica Caprica/pex/ |

Sources inspected:

- https://skse.silverlock.org/ — official classic 1.7.3 archive, obtained 2026-11-13.
- https://github.com/DavidJCobb/skyrim-classic-re/tree/d217bef50272d50bf37b1b9f9a41ab0eb2f787d3
- https://github.com/TES5Edit/TES5Edit/blob/dev-4.1.5/Core/wbDefinitionsTES5.pas
- https://github.com/Orvid/Caprica/tree/e4dee0860914d75e770d3f9ab374f7aba474b701
- https://github.com/Orvid/Champollion/tree/bc961a0bdfb4831f8240e6dacee0818b4bf81e00
- https://github.com/TsudaKageyu/minhook/tree/8af6b4acae5a9388fd742b56fa79ece89d96f823

The bridge detours the physical notification function with MinHook; it does not
patch guessed instruction bytes. A thread-local stack context scopes the standard
TESHitEvent listener to each physical notification. That listener uses the actual
event's bash/block/power flags. At most one qualifying callback per physical call
is accepted. Calls outside that context (including spell/enchantment notifications)
do not generate rewards. Nested physical calls get independent stack contexts.
There is no time window, no actor scan and no periodic update.

The original function is called once, and the event listener always returns
kEvent_Continue. The bridge sends a fixed-name SKSE mod event with sender=the attacking actor and numArg=0.
Papyrus casts sender to Actor, selects player/NPC persistent globals, checks enabled and amount, and calls vanilla RestoreActorValue. The numeric event payload is not trusted as a reward amount.

MinHook's source and BSD license are included. SKSE and game assets are not
redistributed. All new source is provided in this archive; the addresses/layouts
are documented interoperability facts from the above sources.

Important validation boundary: the target entry point/address and call sequence
were checked against published classic reverse-engineering sources, not a local
TESV.exe disassembly. The actual trampoline installation and game behavior still
need validation in Skyrim. Unit/emulation tests are not substitutes for that.

## 1.1.0 MCM and compiler references

- https://github.com/schlangster/skyui/blob/master/dist/Data/Scripts/Source/SKI_ConfigBase.psc
- https://github.com/schlangster/skyui/blob/master/dist/Data/Scripts/Source/SKI_QuestBase.psc
- https://github.com/schlangster/skyui/blob/master/dist/Data/Scripts/Source/SKI_PlayerLoadGameAlias.psc
- https://github.com/russo-2025/papyrus-compiler/releases/tag/2026.03.15

SkyUI supplies the inherited initialization/registration and load-game alias. The new MCM quest attaches that alias separately from the preserved controller. No SkyUI core scripts are bundled. ModEvent v2 replaces v1; the alias unregisters v1 at initialization/load, preventing the old callback registration from remaining active. Settings use four non-constant GLOB records.

The user reported that the previous player-only bridge worked in game. This is evidence for that previous version, not an in-game test of 1.1.0.

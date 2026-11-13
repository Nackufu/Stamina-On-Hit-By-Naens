# Stamina On Hit - By Naens 1.1.0: source for review

This repository contains the source extracted from the Developer directory of the distributed 1.1.0 release. Gameplay source is unchanged. The native build helper now creates its output directory when absent, so a fresh GitHub download builds without relying on empty-folder placeholder files. The source checksum list covers the files published in this repository. It is provided to support manual review of the quarantined Nexus Mods upload. It does not assert that the upload is approved or that its quarantine is a false positive.

## Purpose and implementation

Skyrim Legendary Edition 1.9.32 x86 / SKSE 1.7.3 plugin. A successful physical melee weapon hit sends an SKSE mod callback with the attacking actor as sender. Papyrus restores stamina using separate player/NPC settings. SkyUI 5.1 LE provides the MCM.

The native DLL uses MinHook to detour the physical-hit notification function at 0x006E4060 inside TESV.exe. A thread-local context limits handling to that notification path; it filters out bashes, projectiles, spells and unarmed attacks. Its use of an in-process hook is intentional and documented, but the actual reason for quarantine is not known. The plugin writes a diagnostic log under Documents/My Games/Skyrim/SKSE. It is loaded by SKSE; it is not a standalone injector or installer.

## Start here

- [Native implementation](project/src/plugin.c)
- [Hit filters](project/src/hit_filter.h)
- [Papyrus sources](project/Data/Scripts/Source)
- [Build instructions and toolchain versions](project/docs/BUILD.md)
- [ABI/address provenance](project/docs/ABI_SOURCES.md)
- [Validation scope and limitations](project/docs/VALIDATION.md)
- [MinHook license](project/third_party/minhook/LICENSE.txt)
- [Release and runtime SHA256 hashes](RELEASE_SHA256.json)

## Build the DLL

From this repository root, in a Python 3 environment:

```sh
python -m pip install ziglang==0.17.1 pefile==2024.8.26 unicorn==2.1.4
python project/tools/build_records.py
python project/tools/build_native.py
```

Output: project/Data/SKSE/Plugins/NackufuStaminaOnHitLE.dll. The legacy DLL and ESP filenames are intentional for upgrades.

To compile Papyrus, obtain the compiler listed in project/docs/BUILD.md, then run:

```sh
python project/tools/compile_papyrus.py --compiler /absolute/path/to/papyrus
```

The compile_headers directory contains interface declarations only; never install its files into Skyrim. The official LE Creation Kit alternative is documented in BUILD.md. No Bethesda, SKSE or SkyUI core binaries are redistributed here.

## Tests

After building the DLL and PEX files:

```sh
python project/tools/build_native.py --test
python project/tests/native_emulation.py
python project/tests/validate_artifacts.py
```

Tests use mocks; they do not establish antivirus clearance or prove game stability. Binary timestamps/toolchain environments may differ when rebuilding. RELEASE_SHA256.json identifies the submitted local release, not a guaranteed byte-identical rebuild.

This review bundle intentionally contains source and documentation only, with no compiled DLL/PEX/ESP or nested archives. It is not a replacement game installation package. Source-only packaging is for readable review, not a workaround for Nexus security checks. The original quarantined file should remain available for moderator review.

MinHook's source and license are preserved. No new redistribution license is assigned to the author's own source by this review bundle.

# Rebuilding 1.1.0

The Developer directory is a complete source tree. Run commands from its parent or adapt paths below; here `project` denotes that source-tree root.

## Native DLL and records

Python 3 with `ziglang==0.17.1`, `pefile==2024.8.26`, `unicorn==2.1.4`:

```sh
python project/tools/build_records.py
python project/tools/build_native.py
python project/tools/build_native.py --test
python project/tests/native_emulation.py
```

The release DLL replaces the same legacy filename to prevent two hook DLLs being loaded. Test exports occur only in build/NSH_test.dll, never in Data or the ZIP runtime. MinHook has one upstream unused-parameter warning under the x86 build.

## Papyrus

The supplied PEX files were compiled with russo-2025/papyrus-compiler release 2026.03.15, using only classic Skyrim/SKSE/SkyUI APIs. They use Skyrim big-endian PEX 3.2, game ID 1. This alternative compiler is not Bethesda's Creation Kit compiler. The release advertises SE/AE use; bytecode format and used API compatibility are checked independently here, but actual LE runtime validation remains required.

Source and release:
- https://github.com/russo-2025/papyrus-compiler
- https://github.com/russo-2025/papyrus-compiler/releases/tag/2026.03.15
- Linux archive: papyrus-compiler-ubuntu.tar.gz
- Archive SHA256: d5e72c393ef85a3cd4f839b5bbda52b08bfb358832c36686043e61f5408f736e

```sh
python project/tools/compile_papyrus.py --compiler /absolute/path/to/papyrus
python project/tests/validate_artifacts.py
```

`compile_headers` contains purpose-limited interface declarations, not implementations or game scripts. Never install or compile them into runtime PEX. The SkyUI property declarations use explicit accessors to ensure inherited ModName/Pages compile to property operations rather than access to another script's auto-property backing variable. Native methods in these headers describe call signatures only; the installed Skyrim/SKSE/SkyUI implementations resolve them.

To use Bethesda's official compiler instead, install the LE CK, SKSE 1.7.3 sources and SkyUI 5.1 LE SDK sources under the game's Data/Scripts/Source, then run:

```bat
project\tools\compile_ck.cmd "C:\Games\Skyrim"
```

The official compilation path is provided but was not run in this environment. Do not substitute SE/AE compiler headers with added APIs. No SkyUI or Bethesda core PEX is distributed.

## Independent inspection and package

Champollion commit bc961a0bdfb4831f8240e6dacee0818b4bf81e00 independently decompiled both PEX files. The resulting sources are included in docs for inspection. Re-run decompilation when changing scripts.

```sh
cc -std=c11 -Wall -Wextra project/tests/filter_test.c -o /tmp/nsh_filter_test
/tmp/nsh_filter_test
python project/tests/validate_artifacts.py
python project/tests/native_emulation.py
python project/tools/package.py
```

The ZIP contains runtime files on an explicit allowlist, source and tests under Developer, FOMOD installer metadata, documentation, and SHA256SUMS.json. PEX timestamps may differ on rebuild; records and archive ordering are deterministic. The native build may produce symbol/import-library side files; the packager excludes them.

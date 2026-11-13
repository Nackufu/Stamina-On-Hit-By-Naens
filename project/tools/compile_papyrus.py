#!/usr/bin/env python3
"""Compile only project scripts with russo-2025/papyrus-compiler 2026.03.15."""
from pathlib import Path
import argparse,subprocess
p=argparse.ArgumentParser();p.add_argument('--compiler',required=True);a=p.parse_args()
r=Path(__file__).resolve().parents[1]
subprocess.run([str(Path(a.compiler).resolve()),'compile','-nocache','-h',str(r/'compile_headers'),'-i',str(r/'Data/Scripts/Source'),'-o',str(r/'Data/Scripts')],check=True)
for name in ['NSH_PlayerAlias','NSH_MCM']:
    assert (r/f'Data/Scripts/{name}.pex').read_bytes()[:8]==bytes.fromhex('fa57c0de03020001')
print('PASS: Skyrim LE-compatible big-endian PEX 3.2, game ID 1.')

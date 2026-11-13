#!/usr/bin/env python3
"""Create the install ZIP with a separate, non-installed developer source tree."""
from pathlib import Path
import hashlib
import json
import zipfile
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/'dist/Stamina_On_Hit_By_Naens_1.1.0.zip'
OUTPUT.parent.mkdir(exist_ok=True)
entries={}
def add_tree(folder,prefix):
    for p in sorted(folder.rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts:
            entries[str(Path(prefix)/p.relative_to(folder))]=p.read_bytes()

# Explicit runtime allowlist avoids shipping test DLLs, symbols or import libraries.
runtime=['Nackufu_Stamina_on_Hit_LE.esp','SEQ/Nackufu_Stamina_on_Hit_LE.seq',
         'Scripts/NSH_MCM.pex','Scripts/Source/NSH_MCM.psc','Scripts/NSH_PlayerAlias.pex','Scripts/Source/NSH_PlayerAlias.psc',
         'SKSE/Plugins/NackufuStaminaOnHitLE.dll']
for name in runtime:entries['Data/'+name]=(ROOT/'Data'/name).read_bytes()
add_tree(ROOT/'docs','docs');add_tree(ROOT/'fomod','fomod')
entries['README_TR.md']=(ROOT/'README_TR.md').read_bytes()
for folder in ['compile_headers','src','tools','tests','third_party','OriginalPrototype','docs','fomod']:
    add_tree(ROOT/folder,'Developer/'+folder)
add_tree(ROOT/'Data/Scripts/Source','Developer/Data/Scripts/Source')
entries['Developer/Data/SEQ/.keep']=b''
entries['Developer/Data/SKSE/Plugins/.keep']=b''
entries['Developer/README_TR.md']=(ROOT/'README_TR.md').read_bytes()
checksums={k:hashlib.sha256(v).hexdigest() for k,v in entries.items()}
entries['SHA256SUMS.json']=(json.dumps(checksums,indent=2)+'\n').encode()
for name in ['fomod/info.xml','fomod/ModuleConfig.xml']:ET.fromstring(entries[name])
for element in ET.fromstring(entries['fomod/ModuleConfig.xml']).find('requiredInstallFiles'):
    src=element.attrib['source']
    assert src in entries or any(n.startswith(src+'/') for n in entries)
    dst=element.attrib['destination'].replace('\\','/')
    assert '..' not in Path(dst).parts
with zipfile.ZipFile(OUTPUT,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for name,data in sorted(entries.items()):
        assert '..' not in Path(name).parts and not name.startswith('/')
        zi=zipfile.ZipInfo(name,date_time=(2026,11,13,0,0,0))
        zi.compress_type=zipfile.ZIP_DEFLATED
        zi.external_attr=0o100644<<16
        z.writestr(zi,data)
with zipfile.ZipFile(OUTPUT) as z:
    assert z.testzip() is None
    assert [n for n in z.namelist() if n.lower().endswith('.dll')]==['Data/SKSE/Plugins/NackufuStaminaOnHitLE.dll']
    for name,expected in checksums.items():assert hashlib.sha256(z.read(name)).hexdigest()==expected
print('PASS: FOMOD XML/source paths, runtime allowlist, ZIP CRC and all SHA256 hashes.')
print(OUTPUT)

#!/usr/bin/env python3
"""Build LE Form43 ESP/SEQ. Existing controller and file identity are preserved."""
from pathlib import Path
import struct as s
import json
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'Data'
def pack(fmt,*args):return s.pack('<'+fmt,*args)
def z(t):return t.encode()+b'\0'
def ls(t):return pack('H',len(t.encode()))+t.encode()
def sub(sig,b):return sig.encode()+pack('H',len(b))+b
def record(sig,fid,b):return sig.encode()+pack('IIIIHH',len(b),0,fid,0,43,0)+b
def group(sig,b):return b'GRUP'+pack('I',24+len(b))+sig.encode()+pack('IHHHH',0,0,0,0,0)+b
def script(name):return ls(name)+pack('BH',0,0)
def quest(fid,editor,main,alias):
    vmad=pack('HHH',5,2,bool(main))+(script(main) if main else b'')
    vmad+=pack('BH',2,0)+ls('')+pack('H',1)
    vmad+=pack('HhIHHH',0,0,fid,5,2,1)+script(alias)
    fields=[('EDID',z(editor)),('VMAD',vmad),('FULL',z('Stamina On Hit - By Naens')),
        ('DNAM',pack('HBBII',0x101,0,0,0,0)),('NEXT',b''),('ANAM',pack('I',1)),
        ('ALST',pack('I',0)),('ALID',z('Player')),('FNAM',pack('I',0x210)),
        ('ALFR',pack('I',0x14)),('ALED',b'')]
    return record('QUST',fid,b''.join(sub(k,v) for k,v in fields))
def main():
    globals_=[(0x810,'NSH_PlayerEnabled',1),(0x811,'NSH_NPCEnabled',1),
        (0x812,'NSH_PlayerAmount',10),(0x813,'NSH_NPCAmount',10)]
    glob=b''.join(record('GLOB',0x01000000+i,sub('EDID',z(n))+sub('FNAM',b'f')+sub('FLTV',pack('f',v))) for i,n,v in globals_)
    quests=[(0x01000800,'NSH_Controller',None,'NSH_PlayerAlias'),(0x01000801,'NSH_MCMQuest','NSH_MCM','SKI_PlayerLoadGameAlias')]
    header=record('TES4',0,b''.join([sub('HEDR',pack('fII',1.7,8,0x814)),sub('CNAM',z('Naens')),
        sub('SNAM',z('Stamina On Hit - By Naens 1.1.0. Player and NPC melee-hit stamina; SkyUI MCM. Requires SKSE 1.7.3.')),
        sub('MAST',z('Skyrim.esm')),sub('DATA',pack('Q',0))]))
    DATA.mkdir(exist_ok=True)
    (DATA/'Nackufu_Stamina_on_Hit_LE.esp').write_bytes(header+group('GLOB',glob)+group('QUST',b''.join(quest(*q) for q in quests)))
    (DATA/'SEQ').mkdir(exist_ok=True)
    (DATA/'SEQ/Nackufu_Stamina_on_Hit_LE.seq').write_bytes(pack('II',*(q[0] for q in quests)))
    manifest={'display_name':'Stamina On Hit - By Naens','version':'1.1.0','plugin':'Nackufu_Stamina_on_Hit_LE.esp','format_version':43,'master':'Skyrim.esm',
        'quests':[{'form_id':f'{q[0]:08X}','editor_id':q[1],'quest_script':q[2],'alias_script':q[3],'flags':['Start Game Enabled','Run Once'],'alias_id':0,'forced_reference':'00000014','alias_flags':['Allow Dead','Allow Reserved']} for q in quests],
        'globals':[{'form_id':f'{0x01000000+i:08X}','editor_id':n,'type':'float','default':v,'constant':False} for i,n,v in globals_], 'vanilla_overrides':[]}
    (ROOT/'docs/CK_RECORDS.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('PASS: wrote LE ESP (4 GLOB, 2 QUST) and two-quest SEQ; PEX files untouched.')
if __name__=='__main__':main()

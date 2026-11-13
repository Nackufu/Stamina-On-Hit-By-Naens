#!/usr/bin/env python3
"""Execute real compiled x86 hit bridge with mocked engine/Win32 functions.
This checks calling conventions/context/filter/emission, NOT the actual game.
Requires: pefile, unicorn. First: python tools/build_native.py --test
"""
from pathlib import Path
import struct
import pefile
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_ECX, UC_X86_REG_EIP, UC_X86_REG_ESP

ROOT = Path(__file__).resolve().parents[1]
pe = pefile.PE(str(ROOT/'build/NSH_test.dll'))
uc = Uc(UC_ARCH_X86, UC_MODE_32)
base = pe.OPTIONAL_HEADER.ImageBase
uc.mem_map(base, (pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095)
uc.mem_write(base, pe.get_memory_mapped_image())
uc.mem_map(0x00400000,0x02000000)
uc.mem_map(0x20000000,0x10000)
uc.mem_map(0x30000000,0x10000)
exports = {x.name.decode():base+x.address for x in pe.DIRECTORY_ENTRY_EXPORT.symbols}
pack = lambda *x: struct.pack('<'+'I'*len(x),*x)
u32 = lambda p: struct.unpack('<I',uc.mem_read(p,4))[0]
handlers = {}
tls = {}
rewards = []

def ret(value=0, pop=0):
    sp = uc.reg_read(UC_X86_REG_ESP)
    ra = u32(sp)
    uc.reg_write(UC_X86_REG_EAX,value)
    uc.reg_write(UC_X86_REG_ESP,sp+4+pop)
    uc.reg_write(UC_X86_REG_EIP,ra)

def arg(n): return u32(uc.reg_read(UC_X86_REG_ESP)+4+4*n)
for i,entry in enumerate(x for d in pe.DIRECTORY_ENTRY_IMPORT for x in d.imports):
    addr = 0x20000000+i*16
    uc.mem_write(entry.address,pack(addr))
    name = entry.name.decode() if entry.name else str(entry.ordinal)
    if name == 'TlsGetValue': handlers[addr] = lambda: ret(tls.get(arg(0),0),4)
    elif name == 'TlsSetValue':
        def set_tls(): tls[arg(0)] = arg(1); ret(1,8)
        handlers[addr] = set_tls
    else:
        def unhandled(name=name): raise AssertionError('Unexpected import: '+name)
        handlers[addr] = unhandled

PLAYER, NPC, TARGET, WEAPON, SPELL = 0x02000000,0x02001000,0x02002000,0x02003000,0x02004000
TREF, AREF, EVENT = 0x02005000,0x02005004,0x02006000
ORIGINAL, DISPATCHER = 0x00F00000,0x02007000
uc.mem_write(0x01B2E8E4,pack(PLAYER))
for p in [PLAYER,NPC,TARGET]: uc.mem_write(p+0x12,b'\x3e')
uc.mem_write(WEAPON+0x12,b'\x29')
uc.mem_write(SPELL+0x12,b'\x16')
handlers[0x00451A30] = lambda: ret({0x123:WEAPON,0x456:SPELL}.get(arg(0),0))
def string_ctor():
    ptr = uc.reg_read(UC_X86_REG_ECX)
    uc.mem_write(ptr,pack(arg(0)))
    ret(ptr,4)
handlers[0x00A511C0] = string_ctor
handlers[0x00A511B0] = lambda: ret()
def emit():
    ptr = arg(0)
    e = bytes(uc.mem_read(ptr,16))
    name,arg_,number,sender = struct.unpack('<IIfI',e)
    text = bytes(uc.mem_read(name,24)).split(b'\0')[0]
    rewards.append((text,number,sender))
    ret(0,4)
handlers[0x006EBC10] = emit
def code_hook(uc,address,size,user):
    if address in handlers: handlers[address]()
uc.hook_add(UC_HOOK_CODE,code_hook)

def call(name,*args):
    sp = 0x3000E000
    uc.mem_write(sp,pack(0x2000F000,*args))
    uc.reg_write(UC_X86_REG_ESP,sp)
    uc.emu_start(exports[name],0x2000F000,count=100000)
    assert uc.reg_read(UC_X86_REG_ESP) == sp+4, 'cdecl stack imbalance'

call('NSH_TestSetup',ORIGINAL,DISPATCHER)
def set_original(repeats):
    # The engine's physical sender calls the actual sink, then ret 20 (__thiscall).
    body = b''
    for _ in range(repeats):
        body += b'\x68'+pack(EVENT)+b'\xB8'+pack(exports['NSH_TestEvent'])+b'\xFF\xD0\x83\xC4\x04'
    uc.mem_write(ORIGINAL,body+b'\xC2\x14\x00')
    uc.ctl_remove_cache(ORIGINAL,ORIGINAL+0x1000)

def hit(flags=0,attacker=PLAYER,source=0x123,weapon=1,projectile=0,target=TARGET,repeats=1):
    uc.mem_write(TREF,pack(target)); uc.mem_write(AREF,pack(attacker))
    uc.mem_write(EVENT,struct.pack('<IIIIB3x',target,attacker,source,projectile,flags))
    uc.mem_write(WEAPON+0xF1,bytes([weapon]))
    set_original(repeats)
    before = len(rewards)
    call('NSH_TestPhysical',TREF,AREF,source,projectile)
    assert tls.get(1,0) == 0, 'physical context leaked'
    return len(rewards)-before

for flags in [0,1,2,3,8,9,10,11]:
    assert hit(flags=flags) == 1
for typ in range(1,7): assert hit(weapon=typ) == 1
for typ in [0,7,8,9,10,11,255]: assert hit(weapon=typ) == 0
for flags in [4,5,12,13]: assert hit(flags=flags) == 0
assert hit(attacker=NPC) == 1
assert rewards[-1][2] == NPC
assert hit(attacker=NPC,target=PLAYER) == 1
assert rewards[-1][2] == NPC
assert hit(attacker=SPELL) == 0
assert hit(attacker=0) == 0
assert hit(source=0x456) == 0
assert hit(source=0) == 0
assert hit(projectile=1) == 0
assert hit(target=PLAYER) == 0
assert hit(target=0) == 0
assert hit(repeats=3) == 1
# Two physical calls in the same emulated frame: both count, no cooldown.
assert hit() == 1 and hit() == 1
# Reentrant engine callbacks: nested physical call has its own context.
DEPTH=0x02008000
uc.mem_write(DEPTH,pack(0))
inner=b'\xFF\x05'+pack(DEPTH)
for x in [0,0x123,AREF,TREF]:inner+=b'\x68'+pack(x)
inner+=b'\xB8'+pack(exports['NSH_TestPhysical'])+b'\xFF\xD0\x83\xC4\x10'
inner+=b'\xFF\x0D'+pack(DEPTH)
body=b'\x83\x3D'+pack(DEPTH)+b'\x00\x75'+bytes([len(inner)])+inner
body+=b'\x68'+pack(EVENT)+b'\xB8'+pack(exports['NSH_TestEvent'])+b'\xFF\xD0\x83\xC4\x04\xC2\x14\x00'
uc.mem_write(ORIGINAL,body)
uc.ctl_remove_cache(ORIGINAL,ORIGINAL+0x1000)
before=len(rewards)
call('NSH_TestPhysical',TREF,AREF,0x123,0)
assert len(rewards)-before==2 and tls.get(1,0)==0
before = len(rewards)
call('NSH_TestEvent',EVENT) # enchantment/magic event outside physical path
assert len(rewards) == before
assert all(x[0:2] == (b'NSH_PhysicalMeleeHit_v2',0.0) and x[2] in (PLAYER,NPC) for x in rewards)
print('PASS: compiled x86 bridge, ABI stack balance, player and NPC attacker/weapon/flag filters, repeated callbacks, consecutive and nested hits, context restoration, attacker payload.')

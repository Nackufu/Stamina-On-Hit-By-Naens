#!/usr/bin/env python3
"""Independent ESP/PEX/PE parsers and a small PEX VM with mocked game/SkyUI APIs.
Executes distributed bytecode, not source translations. Does not emulate Skyrim.
"""
from pathlib import Path
import struct
import pefile
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'Data'
class Reader:
    def __init__(self,data,endian):self.data=data;self.pos=0;self.endian=endian
    def raw(self,n):
        b=self.data[self.pos:self.pos+n];assert len(b)==n;self.pos+=n;return b
    def get(self,fmt):
        v=struct.unpack(self.endian+fmt,self.raw(struct.calcsize(self.endian+fmt)))
        return v[0] if len(v)==1 else v
    def string(self):return self.raw(self.get('H')).decode()
    def done(self):assert self.pos==len(self.data),(self.pos,len(self.data))
def parse_pex(name):
    p=Reader((DATA/f'Scripts/{name}.pex').read_bytes(),'>')
    assert p.get('IBBH')==(0xFA57C0DE,3,2,1)
    p.get('Q');assert p.string().endswith(name+'.psc');p.string();p.string()
    strings=[p.string() for _ in range(p.get('H'))]
    def idx():return strings[p.get('H')]
    def val():
        t=p.get('B')
        return (t,None if t==0 else idx() if t in (1,2) else p.get({3:'i',4:'f',5:'B'}[t]))
    if p.get('B'):
        p.get('Q')
        for _ in range(p.get('H')):
            idx();idx();idx();p.get('B');p.raw(2*p.get('H'))
    for _ in range(p.get('H')):idx();p.get('B')
    assert p.get('H')==1 and idx()==name
    size=p.get('I');start=p.pos
    parent=idx();idx();p.get('I');idx();variables={};types={}
    for _ in range(p.get('H')):
        n=idx().lower();types[n]=idx().lower();p.get('I');variables[n]=val()[1]
    assert p.get('H')==0 # inherits SkyUI properties, no local properties
    assert p.get('H')==1 and idx()==''
    counts=[0]+[3]*9+[2]*5+[3]*5+[1,2,2,3,2,3,1,3,3,3,2,2,3,3,4,4]
    funcs={}
    for _ in range(p.get('H')):
        n=idx().lower();result=idx();idx();p.get('I');p.get('B')
        params=[(idx().lower(),idx().lower()) for _ in range(p.get('H'))]
        locals_=[(idx().lower(),idx().lower()) for _ in range(p.get('H'))]
        code=[]
        for _ in range(p.get('H')):
            op=p.get('B');assert op<len(counts),'non-LE opcode'
            args=[val() for _ in range(counts[op])];extra=[]
            if op in (23,24,25):
                count=val();assert count[0]==3;extra=[val() for _ in range(count[1])]
            code.append((op,args,extra))
        for pc,(op,a,_) in enumerate(code):
            if op in (20,21,22):assert 0<=pc+a[-1][1]<=len(code)
        funcs[n]=(params,locals_,code)
    assert p.pos-start in (size,size-4),(p.pos-start,size)
    p.done();return variables,types,funcs,parent
class Actor:
    def __init__(self):self.rewards=[]
class Global:
    def __init__(self,value):self.value=float(value)
class VM:
    def __init__(self,name,globals_,player):
        self.vars,self.types,self.funcs,self.parent=parse_pex(name)
        self.globals=globals_;self.player=player;self.props={};self.calls=[];self.registrations=set();self.option=0
    def run(self,name,*args):
        params,locals_,code=self.funcs[name.lower()]
        env={n:None for n,t in locals_};env.update(zip((n for n,t in params),args));env['self']=self
        types=dict(self.types,**dict(params+locals_));pc=0;steps=0
        def get(v):
            if v[0]!=1:return v[1]
            n=v[1].lower();return env[n] if n in env else self.vars.get(n)
        def put(v,value):
            n=v[1].lower()
            if n in self.vars:self.vars[n]=value
            else:env[n]=value
        while pc<len(code):
            steps+=1;assert steps<10000
            op,a,extra=code[pc]
            if op==0:pass
            elif op==10:put(a[0],not get(a[1]))
            elif op==13:put(a[0],get(a[1]))
            elif op==14:
                v=get(a[1]);t=types.get(a[0][1].lower(),'')
                if t=='actor':v=v if isinstance(v,Actor) else None
                elif t=='globalvariable':v=v if isinstance(v,Global) else None
                elif t=='bool':v=bool(v)
                elif t=='float':v=float(v or 0)
                elif t=='int':v=int(v or 0)
                elif t=='string':v=str(v or '')
                put(a[0],v)
            elif op in (15,16,17,18,19):
                x,y=get(a[1]),get(a[2])
                put(a[0],{15:lambda:x==y,16:lambda:x<y,17:lambda:x<=y,18:lambda:x>y,19:lambda:x>=y}[op]())
            elif op in (20,21,22):
                if op==20 or bool(get(a[0]))==(op==21):pc+=get(a[-1]);continue
            elif op==23:
                recv=get(a[1]);method=a[0][1].lower();values=[get(v) for v in extra]
                if recv is self and method in self.funcs:out=self.run(method,*values)
                elif isinstance(recv,Global):
                    assert method in ('getvalue','setvalue')
                    if method=='setvalue':recv.value=values[0];out=None
                    else:out=recv.value
                elif isinstance(recv,Actor):
                    assert method=='restoreactorvalue' and values[0]=='Stamina';recv.rewards.append(values[1]);out=None
                elif recv is self:
                    self.calls.append((method,values));out=None
                    if method=='registerformodevent':self.registrations.add(tuple(values))
                    elif method=='unregisterformodevent':self.registrations={x for x in self.registrations if x[0]!=values[0]}
                    elif method.startswith('add') and method.endswith('option'):self.option+=1;out=self.option
                    else:assert method.startswith('set') or method in ('onendstate','onbeginstate'),method
                else:raise AssertionError(('bad receiver',recv,method))
                put(a[2],out)
            elif op==25:
                assert a[0][1].lower()=='game';method=a[1][1].lower();values=[get(v) for v in extra]
                if method=='getplayer':out=self.player
                else:
                    assert method=='getformfromfile' and values[1]=='Nackufu_Stamina_on_Hit_LE.esp';out=self.globals.get(values[0])
                put(a[2],out)
            elif op==26:return get(a[0])
            elif op==28:assert get(a[1]) is self;put(a[2],self.props.get(a[0][1].lower()))
            elif op==29:assert get(a[1]) is self;self.props[a[0][1].lower()]=get(a[2])
            elif op==30:put(a[0],[None]*get(a[1]))
            elif op==32:put(a[0],get(a[1])[get(a[2])])
            elif op==33:get(a[0])[get(a[1])]=get(a[2])
            else:raise AssertionError(('unsupported opcode',op))
            pc+=1
        return None

globals_={i:Global(v) for i,v in zip(range(0x810,0x814),(1,1,10,10))}
player,npc=Actor(),Actor();alias=VM('NSH_PlayerAlias',globals_,player);mcm=VM('NSH_MCM',globals_,player)
assert alias.parent=='ReferenceAlias' and mcm.parent=='SKI_ConfigBase'
alias.registrations.add(('NSH_PhysicalMeleeHit_v1','OnPhysicalMeleeHit'))
alias.run('OnInit');alias.run('OnPlayerLoadGame')
assert alias.registrations=={('NSH_PhysicalMeleeHit_v2','OnPhysicalMeleeHit')}
def hit(who):alias.run('OnPhysicalMeleeHit','NSH_PhysicalMeleeHit_v2','',999,who)
hit(player);hit(npc);hit(None);hit(object());assert player.rewards==[10] and npc.rewards==[10]
mcm.run('OnConfigInit');assert mcm.props=={'modname':'Stamina On Hit - By Naens','pages':['Settings']}
assert mcm.run('GetVersion')==110
mcm.run('OnPageReset','Settings')
pt,nt,ps,ns=[mcm.vars[x] for x in ['_playertoggle','_npctoggle','_playerslider','_npcslider']]
assert len(set((pt,nt,ps,ns)))==4
mcm.run('OnOptionSliderAccept',ps,23.0);mcm.run('OnOptionSliderAccept',ns,7.0)
hit(player);hit(npc);assert player.rewards[-1]==23 and npc.rewards[-1]==7
mcm.run('OnOptionSelect',pt);before=len(player.rewards);hit(player);hit(npc)
assert len(player.rewards)==before and npc.rewards[-1]==7
mcm.run('OnOptionSelect',nt);before=len(npc.rewards);hit(npc);assert len(npc.rewards)==before
mcm.run('OnOptionSelect',pt);mcm.run('OnOptionSelect',nt)
# Load/version refresh retains settings and registration.
alias.run('OnPlayerLoadGame');mcm.run('OnVersionUpdate',109)
assert [globals_[i].value for i in range(0x810,0x814)]==[1,1,23,7]
for opt in (ps,ns):
    mcm.run('OnOptionSliderOpen',opt)
    assert ('setsliderdialogrange',[0.0,100.0]) in mcm.calls
    assert ('setsliderdialoginterval',[1.0]) in mcm.calls
mcm.run('OnOptionSliderAccept',ps,-5);mcm.run('OnOptionSliderAccept',ns,500)
before=len(player.rewards);hit(player);hit(npc);assert len(player.rewards)==before and npc.rewards[-1]==100
# Guard against out-of-range settings edited via console; missing globals fail closed.
globals_[0x812].value=999;hit(player);assert player.rewards[-1]==100
globals_[0x812].value=-1;before=len(player.rewards);hit(player);assert len(player.rewards)==before
assert alias.run('ReadAmount',None,globals_[0x812])==0
assert alias.run('ReadAmount',globals_[0x810],None)==0
for opt in (pt,nt,ps,ns):mcm.run('OnOptionDefault',opt);mcm.run('OnOptionHighlight',opt)
assert [globals_[i].value for i in range(0x810,0x814)]==[1,1,10,10]
before=[g.value for g in globals_.values()];mcm.run('OnOptionSliderAccept',-999,60)
assert [g.value for g in globals_.values()]==before
# A new alias instance also resolves saved settings.
globals_[0x812].value=31
reload=VM('NSH_PlayerAlias',globals_,player);reload.run('OnPlayerLoadGame');reload.run('OnPhysicalMeleeHit','event','',0,player)
assert player.rewards[-1]==31
print('PASS: both real PEX files parsed/executed; registration migration, attacker routing, independent toggles/amounts, MCM pages/defaults/range/clamps and reload persistence.')

e=Reader((DATA/'Nackufu_Stamina_on_Hit_LE.esp').read_bytes(),'<')
def read_record(expected):
    assert e.raw(4)==expected
    length,flags,fid,revision,version,unknown=e.get('IIIIHH');assert version==43 and flags==0
    body=Reader(e.raw(length),'<');fields=[]
    while body.pos<len(body.data):
        sig=body.raw(4);fields.append((sig,body.raw(body.get('H'))))
    body.done();return fid,dict(fields)
fid,header=read_record(b'TES4');assert fid==0 and header[b'MAST']==b'Skyrim.esm\0'
assert struct.unpack('<fII',header[b'HEDR'])[1:]==(8,0x814)
for sig,ids in [(b'GLOB',range(0x01000810,0x01000814)),(b'QUST',range(0x01000800,0x01000802))]:
    assert e.raw(4)==b'GRUP';size=e.get('I');start=e.pos-8;assert e.raw(4)==sig;assert e.get('I')==0;e.raw(8)
    for expected in ids:
        fid,f=read_record(sig);assert fid==expected
        if sig==b'GLOB':
            assert f[b'FNAM']==b'f';assert struct.unpack('<f',f[b'FLTV'])[0]==(1 if fid<0x01000812 else 10)
        else:
            assert f[b'EDID']==(b'NSH_Controller\0' if fid==0x01000800 else b'NSH_MCMQuest\0')
            assert struct.unpack('<H',f[b'DNAM'][:2])[0]==0x101
            assert f[b'ALFR']==struct.pack('<I',0x14) and f[b'FNAM']==struct.pack('<I',0x210)
            assert f[b'ANAM']==struct.pack('<I',1) and f[b'ALST']==b'\0'*4
            v=Reader(f[b'VMAD'],'<');assert v.get('HHH')==(5,2,int(fid==0x01000801))
            if fid==0x01000801:assert v.string()=='NSH_MCM' and v.get('BH')==(0,0)
            assert v.get('BH')==(2,0) and v.string()=='' and v.get('H')==1
            assert v.get('HhIHHH')==(0,0,fid,5,2,1)
            assert v.string()==('NSH_PlayerAlias' if fid==0x01000800 else 'SKI_PlayerLoadGameAlias')
            assert v.get('BH')==(0,0);v.done()
    assert e.pos-start==size
e.done()
assert (DATA/'SEQ/Nackufu_Stamina_on_Hit_LE.seq').read_bytes()==struct.pack('<II',0x01000800,0x01000801)
print('PASS: ESP Form43, four persistent globals, two quests, VMAD scripts, safe alias flags, two-entry SEQ and no vanilla overrides.')
dll=pefile.PE(str(DATA/'SKSE/Plugins/NackufuStaminaOnHitLE.dll'))
assert dll.FILE_HEADER.Machine==0x14c and dll.OPTIONAL_HEADER.Magic==0x10b
assert {x.name.decode() for x in dll.DIRECTORY_ENTRY_EXPORT.symbols}=={'SKSEPlugin_Query','SKSEPlugin_Load'}
imports={x.dll.decode() for x in dll.DIRECTORY_ENTRY_IMPORT}
assert all(x in ['KERNEL32.dll','SHELL32.dll'] or x.startswith('api-ms-win-crt-') for x in imports)
print('PASS: production PE32 x86 DLL, exact SKSE exports, system imports only; no test exports.')

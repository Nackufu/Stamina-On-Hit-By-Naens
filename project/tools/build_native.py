#!/usr/bin/env python3
"""Build an x86 Windows DLL with Zig 0.17.1 (python package ziglang).
For the real game use the release DLL, never the --test DLL.
"""
from pathlib import Path
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[1]
test = '--test' in sys.argv
outdir = ROOT/'build'
outdir.mkdir(exist_ok=True)
out = outdir/('NSH_test.dll' if test else 'NackufuStaminaOnHitLE.dll')
mh = ROOT/'third_party/minhook'
cmd = [sys.executable,'-m','ziglang','cc','-target','x86-windows-gnu','-shared','-O2','-Wall','-Wextra']
if test: cmd.append('-DNSH_TEST')
cmd += ['-I'+str(mh/'include'),'-I'+str(mh/'src'),str(ROOT/'src/plugin.c')]
cmd += [str(mh/'src'/x) for x in ['buffer.c','hook.c','trampoline.c','hde/hde32.c']]
cmd += ['-lshell32','-o',str(out)]
subprocess.run(cmd,check=True)
if not test:
    import shutil
    shutil.copy2(out,ROOT/'Data/SKSE/Plugins'/out.name)
print(out)

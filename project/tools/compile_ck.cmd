@echo off
setlocal
rem Requires LE CK + SKSE 1.7.3 + SkyUI 5.1 LE SDK script sources.
if "%~1"=="" (
  echo Usage: compile_ck.cmd "C:\Games\Skyrim"
  exit /b 2
)
set "NSH_SKYRIM=%~1"
set "NSH_ROOT=%~dp0.."
for %%S in (NSH_PlayerAlias NSH_MCM) do (
  "%NSH_SKYRIM%\Papyrus Compiler\PapyrusCompiler.exe" "%NSH_ROOT%\Data\Scripts\Source\%%S.psc" -f="TESV_Papyrus_Flags.flg" -i="%NSH_SKYRIM%\Data\Scripts\Source;%NSH_ROOT%\Data\Scripts\Source" -o="%NSH_ROOT%\Data\Scripts"
  if errorlevel 1 exit /b 1
)
exit /b 0

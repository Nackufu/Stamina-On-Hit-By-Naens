ScriptName NSH_MCM Extends SKI_ConfigBase

;-- Variables ---------------------------------------
GlobalVariable _playerEnabled
GlobalVariable _npcEnabled
GlobalVariable _playerAmount
GlobalVariable _npcAmount
Int _playerToggle = -1
Int _npcToggle = -1
Int _playerSlider = -1
Int _npcSlider = -1

;-- Functions ---------------------------------------

; Skipped compiler generated GetState

; Skipped compiler generated GotoState

Int Function GetVersion()
  Return 110
EndFunction

Function ResolveSettings()
  _playerEnabled = Game.GetFormFromFile(2064, "Nackufu_Stamina_on_Hit_LE.esp") as GlobalVariable
  _npcEnabled = Game.GetFormFromFile(2065, "Nackufu_Stamina_on_Hit_LE.esp") as GlobalVariable
  _playerAmount = Game.GetFormFromFile(2066, "Nackufu_Stamina_on_Hit_LE.esp") as GlobalVariable
  _npcAmount = Game.GetFormFromFile(2067, "Nackufu_Stamina_on_Hit_LE.esp") as GlobalVariable
EndFunction

Function OnConfigInit()
  Self.ModName = "Stamina On Hit - By Naens"
  Self.Pages = new String[1]
  Self.Pages[0] = "Settings"
  Self.ResolveSettings()
EndFunction

Function OnVersionUpdate(Int a_version)
  Self.ModName = "Stamina On Hit - By Naens"
  Self.ResolveSettings()
EndFunction

Function OnPageReset(String a_page)
  Self.ResolveSettings()
  If !_playerEnabled as Bool || !_npcEnabled as Bool || !_playerAmount as Bool || !_npcAmount as Bool
    Self.AddHeaderOption("Settings unavailable - check the ESP", 0)
    Return 
  EndIf
  Self.SetCursorFillMode(2)
  Self.SetCursorPosition(0)
  Self.AddHeaderOption("PLAYER", 0)
  _playerToggle = Self.AddToggleOption("Enable for player", _playerEnabled.GetValue() >= 0.5, 0)
  _playerSlider = Self.AddSliderOption("Stamina per hit", _playerAmount.GetValue(), "{0}", 0)
  Self.SetCursorPosition(1)
  Self.AddHeaderOption("NPCs", 0)
  _npcToggle = Self.AddToggleOption("Enable for NPCs", _npcEnabled.GetValue() >= 0.5, 0)
  _npcSlider = Self.AddSliderOption("Stamina per hit", _npcAmount.GetValue(), "{0}", 0)
EndFunction

Function ToggleSetting(GlobalVariable setting, Int optionID)
  If setting.GetValue() >= 0.5
    setting.SetValue(0.0)
  Else
    setting.SetValue(1.0)
  EndIf
  Self.SetToggleOptionValue(optionID, setting.GetValue() >= 0.5, False)
EndFunction

Function OnOptionSelect(Int a_option)
  If a_option == _playerToggle
    Self.ToggleSetting(_playerEnabled, a_option)
  ElseIf a_option == _npcToggle
    Self.ToggleSetting(_npcEnabled, a_option)
  EndIf
EndFunction

Function OnOptionSliderOpen(Int a_option)
  If a_option == _playerSlider
    Self.SetSliderDialogStartValue(_playerAmount.GetValue())
  ElseIf a_option == _npcSlider
    Self.SetSliderDialogStartValue(_npcAmount.GetValue())
  Else
    Return 
  EndIf
  Self.SetSliderDialogDefaultValue(10.0)
  Self.SetSliderDialogRange(0.0, 100.0)
  Self.SetSliderDialogInterval(1.0)
EndFunction

Function OnOptionSliderAccept(Int a_option, Float a_value)
  If a_value < 0.0
    a_value = 0.0
  ElseIf a_value > 100.0
    a_value = 100.0
  EndIf
  If a_option == _playerSlider
    _playerAmount.SetValue(a_value)
  ElseIf a_option == _npcSlider
    _npcAmount.SetValue(a_value)
  Else
    Return 
  EndIf
  Self.SetSliderOptionValue(a_option, a_value, "{0}", False)
EndFunction

Function OnOptionDefault(Int a_option)
  If a_option == _playerToggle
    _playerEnabled.SetValue(1.0)
    Self.SetToggleOptionValue(a_option, True, False)
  ElseIf a_option == _npcToggle
    _npcEnabled.SetValue(1.0)
    Self.SetToggleOptionValue(a_option, True, False)
  ElseIf a_option == _playerSlider
    _playerAmount.SetValue(10.0)
    Self.SetSliderOptionValue(a_option, 10.0, "{0}", False)
  ElseIf a_option == _npcSlider
    _npcAmount.SetValue(10.0)
    Self.SetSliderOptionValue(a_option, 10.0, "{0}", False)
  EndIf
EndFunction

Function OnOptionHighlight(Int a_option)
  If a_option == _playerToggle
    Self.SetInfoText("Restore stamina when your melee weapon hits an actor. Blocked and power attacks count.")
  ElseIf a_option == _npcToggle
    Self.SetInfoText("Includes followers and enemies using melee weapons. Stamina goes to the attacker, not the victim.")
  ElseIf a_option == _playerSlider
    Self.SetInfoText("Player stamina restored per physical hit. Default: 10. Range: 0-100. Zero disables the refund.")
  ElseIf a_option == _npcSlider
    Self.SetInfoText("NPC stamina restored per physical hit. Default: 10. Range: 0-100. Power attacks still cost stamina.")
  EndIf
EndFunction

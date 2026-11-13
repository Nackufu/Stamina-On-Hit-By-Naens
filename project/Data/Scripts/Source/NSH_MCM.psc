Scriptname NSH_MCM extends SKI_ConfigBase

GlobalVariable _playerEnabled
GlobalVariable _npcEnabled
GlobalVariable _playerAmount
GlobalVariable _npcAmount
Int _playerToggle = -1
Int _npcToggle = -1
Int _playerSlider = -1
Int _npcSlider = -1

Int Function GetVersion()
    Return 110
EndFunction

Function ResolveSettings()
    _playerEnabled = Game.GetFormFromFile(0x810, "Nackufu_Stamina_on_Hit_LE.esp") as GlobalVariable
    _npcEnabled = Game.GetFormFromFile(0x811, "Nackufu_Stamina_on_Hit_LE.esp") as GlobalVariable
    _playerAmount = Game.GetFormFromFile(0x812, "Nackufu_Stamina_on_Hit_LE.esp") as GlobalVariable
    _npcAmount = Game.GetFormFromFile(0x813, "Nackufu_Stamina_on_Hit_LE.esp") as GlobalVariable
EndFunction

Event OnConfigInit()
    ModName = "Stamina On Hit - By Naens"
    Pages = new String[1]
    Pages[0] = "Settings"
    ResolveSettings()
EndEvent

Event OnVersionUpdate(Int a_version)
    ; Keep saved values; only refresh references and labels.
    ModName = "Stamina On Hit - By Naens"
    ResolveSettings()
EndEvent

Event OnPageReset(String a_page)
    ResolveSettings()
    If !_playerEnabled || !_npcEnabled || !_playerAmount || !_npcAmount
        AddHeaderOption("Settings unavailable - check the ESP")
        Return
    EndIf
    SetCursorFillMode(2)
    SetCursorPosition(0)
    AddHeaderOption("PLAYER")
    _playerToggle = AddToggleOption("Enable for player", _playerEnabled.GetValue() >= 0.5)
    _playerSlider = AddSliderOption("Stamina per hit", _playerAmount.GetValue(), "{0}")
    SetCursorPosition(1)
    AddHeaderOption("NPCs")
    _npcToggle = AddToggleOption("Enable for NPCs", _npcEnabled.GetValue() >= 0.5)
    _npcSlider = AddSliderOption("Stamina per hit", _npcAmount.GetValue(), "{0}")
EndEvent

Function ToggleSetting(GlobalVariable setting, Int optionID)
    If setting.GetValue() >= 0.5
        setting.SetValue(0.0)
    Else
        setting.SetValue(1.0)
    EndIf
    SetToggleOptionValue(optionID, setting.GetValue() >= 0.5)
EndFunction

Event OnOptionSelect(Int a_option)
    If a_option == _playerToggle
        ToggleSetting(_playerEnabled, a_option)
    ElseIf a_option == _npcToggle
        ToggleSetting(_npcEnabled, a_option)
    EndIf
EndEvent

Event OnOptionSliderOpen(Int a_option)
    If a_option == _playerSlider
        SetSliderDialogStartValue(_playerAmount.GetValue())
    ElseIf a_option == _npcSlider
        SetSliderDialogStartValue(_npcAmount.GetValue())
    Else
        Return
    EndIf
    SetSliderDialogDefaultValue(10.0)
    SetSliderDialogRange(0.0, 100.0)
    SetSliderDialogInterval(1.0)
EndEvent

Event OnOptionSliderAccept(Int a_option, Float a_value)
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
    SetSliderOptionValue(a_option, a_value, "{0}")
EndEvent

Event OnOptionDefault(Int a_option)
    If a_option == _playerToggle
        _playerEnabled.SetValue(1.0)
        SetToggleOptionValue(a_option, True)
    ElseIf a_option == _npcToggle
        _npcEnabled.SetValue(1.0)
        SetToggleOptionValue(a_option, True)
    ElseIf a_option == _playerSlider
        _playerAmount.SetValue(10.0)
        SetSliderOptionValue(a_option, 10.0, "{0}")
    ElseIf a_option == _npcSlider
        _npcAmount.SetValue(10.0)
        SetSliderOptionValue(a_option, 10.0, "{0}")
    EndIf
EndEvent

Event OnOptionHighlight(Int a_option)
    If a_option == _playerToggle
        SetInfoText("Restore stamina when your melee weapon hits an actor. Blocked and power attacks count.")
    ElseIf a_option == _npcToggle
        SetInfoText("Includes followers and enemies using melee weapons. Stamina goes to the attacker, not the victim.")
    ElseIf a_option == _playerSlider
        SetInfoText("Player stamina restored per physical hit. Default: 10. Range: 0-100. Zero disables the refund.")
    ElseIf a_option == _npcSlider
        SetInfoText("NPC stamina restored per physical hit. Default: 10. Range: 0-100. Power attacks still cost stamina.")
    EndIf
EndEvent

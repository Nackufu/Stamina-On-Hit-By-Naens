Scriptname NSH_PlayerAlias extends ReferenceAlias

; One player alias receives physical notifications for ALL attackers.
; Script name and controller FormID are retained for upgrades from v1.
GlobalVariable _playerEnabled
GlobalVariable _npcEnabled
GlobalVariable _playerAmount
GlobalVariable _npcAmount

Function Initialize()
    _playerEnabled = Game.GetFormFromFile(0x810, "Nackufu_Stamina_on_Hit_LE.esp") as GlobalVariable
    _npcEnabled = Game.GetFormFromFile(0x811, "Nackufu_Stamina_on_Hit_LE.esp") as GlobalVariable
    _playerAmount = Game.GetFormFromFile(0x812, "Nackufu_Stamina_on_Hit_LE.esp") as GlobalVariable
    _npcAmount = Game.GetFormFromFile(0x813, "Nackufu_Stamina_on_Hit_LE.esp") as GlobalVariable
    UnregisterForModEvent("NSH_PhysicalMeleeHit_v1")
    RegisterForModEvent("NSH_PhysicalMeleeHit_v2", "OnPhysicalMeleeHit")
EndFunction

Event OnInit()
    Initialize()
EndEvent

Event OnPlayerLoadGame()
    Initialize()
EndEvent

Event OnPhysicalMeleeHit(String eventName, String strArg, Float numArg, Form sender)
    Actor attacker = sender as Actor
    If !attacker
        Return
    EndIf
    If !_playerEnabled
        Initialize()
    EndIf
    Float amount = RewardFor(attacker)
    If amount > 0.0
        attacker.RestoreActorValue("Stamina", amount)
    EndIf
EndEvent

Float Function RewardFor(Actor attacker)
    If attacker == Game.GetPlayer()
        Return ReadAmount(_playerEnabled, _playerAmount)
    EndIf
    Return ReadAmount(_npcEnabled, _npcAmount)
EndFunction

Float Function ReadAmount(GlobalVariable enabledSetting, GlobalVariable amountSetting)
    If !enabledSetting
        Return 0.0
    EndIf
    If !amountSetting
        Return 0.0
    EndIf
    If enabledSetting.GetValue() < 0.5
        Return 0.0
    EndIf
    Float amount = amountSetting.GetValue()
    If amount > 100.0
        Return 100.0
    EndIf
    If amount < 0.0
        Return 0.0
    EndIf
    Return amount
EndFunction

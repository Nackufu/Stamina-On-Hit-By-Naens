ScriptName NSH_PlayerAlias Extends ReferenceAlias

;-- Variables ---------------------------------------
GlobalVariable _playerEnabled
GlobalVariable _npcEnabled
GlobalVariable _playerAmount
GlobalVariable _npcAmount

;-- Functions ---------------------------------------

; Skipped compiler generated GetState

; Skipped compiler generated GotoState

Function Initialize()
  _playerEnabled = Game.GetFormFromFile(2064, "Nackufu_Stamina_on_Hit_LE.esp") as GlobalVariable
  _npcEnabled = Game.GetFormFromFile(2065, "Nackufu_Stamina_on_Hit_LE.esp") as GlobalVariable
  _playerAmount = Game.GetFormFromFile(2066, "Nackufu_Stamina_on_Hit_LE.esp") as GlobalVariable
  _npcAmount = Game.GetFormFromFile(2067, "Nackufu_Stamina_on_Hit_LE.esp") as GlobalVariable
  Self.UnregisterForModEvent("NSH_PhysicalMeleeHit_v1")
  Self.RegisterForModEvent("NSH_PhysicalMeleeHit_v2", "OnPhysicalMeleeHit")
EndFunction

Event OnInit()
  Self.Initialize()
EndEvent

Event OnPlayerLoadGame()
  Self.Initialize()
EndEvent

Function OnPhysicalMeleeHit(String eventName, String strArg, Float numArg, Form sender)
  Actor attacker = sender as Actor
  If !attacker as Bool
    Return 
  EndIf
  If !_playerEnabled as Bool
    Self.Initialize()
  EndIf
  Float amount = Self.RewardFor(attacker)
  If amount > 0.0
    attacker.RestoreActorValue("Stamina", amount)
  EndIf
EndFunction

Float Function RewardFor(Actor attacker)
  If attacker == Game.GetPlayer()
    Return Self.ReadAmount(_playerEnabled, _playerAmount)
  EndIf
  Return Self.ReadAmount(_npcEnabled, _npcAmount)
EndFunction

Float Function ReadAmount(GlobalVariable enabledSetting, GlobalVariable amountSetting)
  If !enabledSetting as Bool
    Return 0.0
  EndIf
  If !amountSetting as Bool
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

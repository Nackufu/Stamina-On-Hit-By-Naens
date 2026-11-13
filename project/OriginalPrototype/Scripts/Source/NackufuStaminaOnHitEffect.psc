Scriptname NackufuStaminaOnHitEffect extends ActiveMagicEffect

; Attach to a Script-archetype Magic Effect delivered by a player's
; Apply Combat Hit Spell perk entry point.
; Restores stamina only to the player, regardless of who is targeted.

Float Property StaminaPerHit = 10.0 Auto

Event OnEffectStart(Actor akTarget, Actor akCaster)
    Actor playerRef = Game.GetPlayer()
    If akCaster == playerRef
        playerRef.RestoreActorValue("Stamina", StaminaPerHit)
    EndIf
EndEvent

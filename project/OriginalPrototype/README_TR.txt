NACKUFU - STAMINA ON HIT LE (PROTOTIP KAYNAK)
==========================================
ONEMLI: Bu ZIP OYNANABILIR MOD DEGILDIR. ESP ve derlenmis PEX yoktur.
Skyrim Legendary Edition Creation Kit ile asagidaki kayitlari olusturup Papyrus scriptini derlemeniz gerekir.

HEDEF
- Yalnizca oyuncunun yakin dovus silah isabetlerinde +10 stamina.
- Bloklu ve guclu isabetler dahil; iskada yok.
- NPC oyuncuya vursa bile kazanc yok.

CREATION KIT KURULUM PLANI
1) Skyrim LE Creation Kit'te Skyrim.esm yukleyip yeni plugin acin.
2) Yeni Magic Effect: EditorID NSH_HitEffect.
   Archetype: Script, hedef: Target Actor, sure: 1 saniye, zararsiz etki.
   NackufuStaminaOnHitEffect scriptini ekleyin ve derleyin.
   StaminaPerHit property degerini 10.0 yapin.
3) Yeni Spell: NSH_HitSpell. Fire-and-Forget, Contact/Target Actor.
   Yalnizca NSH_HitEffect ekleyin.
4) Yeni Perk: NSH_PlayerOnHitPerk. Entry Point:
   Apply Combat Hit Spell -> NSH_HitSpell.
   Perk entry point kosullarinda uygun yakin dovus silahlarini filtreleyin.
   Her iki silah turu, blok ve power attack dahil; yay ve buyuyu haric tutun.
5) Perki oyuna vermek icin konsolda (ESP form ID belirlendikten sonra):
   player.addperk <perk_form_id>
6) Kontrol: stamina 30 puan eksikken NPC'ye tek, bloklu ve guclu vurun;
   ayrica iskayi, yay ve NPC saldirisini test edin.

SINIRLAMALAR / DIKKAT
- Papyrus onEffectStart, perk ile gelen buyu efektinde her tetiklemede
  calisir. Modlu/enchanted silahlarda coklu uygulama ihtimali test edilmeli.
- Apply Combat Hit Spell entry point bazi perk overhaul modlari ile
  cakisma yaratabilir ve bir hit icin birden fazla spell calismayabilir.
- Creation Kit filtre ve spell alanlari yerel CK surumune gore kontrol edilmeli.
- Oyunda test edilmedi: kusursuz calisma garantisi yoktur.
- Bu kaynak Skyrim SE/AE icin hazirlanmamistir.
- Vanilla Papyrus fonksiyonlari kullanilir; harici SKSE script bagimliligi yok.

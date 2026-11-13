# Creation Kit kayıtları — 1.1.0

`Nackufu_Stamina_on_Hit_LE.esp`, Skyrim.esm master'ı olan Form 43 eklentidir.
Kayıtlar programatik üretilip bağımsız ayrıştırıcı ile kontrol edildi; bu ortamda Creation Kit arayüzünde açılıp kaydedilmedi.

| Yerel ID | Tür / EditorID | İçerik |
|---|---|---|
| 000800 | QUST / NSH_Controller | Önceki sürümle aynı; Player alias'ında NSH_PlayerAlias |
| 000801 | QUST / NSH_MCMQuest | Quest scripti NSH_MCM; Player alias'ında SkyUI'nin SKI_PlayerLoadGameAlias scripti |
| 000810 | GLOB / NSH_PlayerEnabled | Float, varsayılan 1, constant değil |
| 000811 | GLOB / NSH_NPCEnabled | Float, varsayılan 1, constant değil |
| 000812 | GLOB / NSH_PlayerAmount | Float, varsayılan 10, constant değil |
| 000813 | GLOB / NSH_NPCAmount | Float, varsayılan 10, constant değil |

İki quest de Start Game Enabled + Run Once, priority 0 kullanır. Her birindeki alias 0: forced reference PlayerRef 00000014, Allow Dead + Allow Reserved. Essential ve Protected bayrakları yoktur. Stage, objective, fragment, condition, perk, magic effect veya spell eklenmez.

VMAD sürüm 5 / object format 2. Scriptlerin CK'de doldurulacak property bağlantısı yoktur; global kayıtlar SKSE GetFormFromFile ile çözülür. MCM'nin taban scriptleri SkyUI tarafından sağlanır. SkyUI.esp form referansı olmadığı için ek master gerekmez.

SEQ iki quest'i de içerir. Dosya içinde Skyrim.esm master indeks 00, bu eklenti 01 olduğu için kayıtlar 01000800/01000801 olarak yazılır; çalışma sırasında gerçek yükleme sırasına taşınırlar. Papyrus yalnızca yerel ID kullanır.

CK'de düzenleme için LE Creation Kit, SKSE 1.7.3 ve SkyUI 5.1 LE script kaynakları gereklidir. `tools/compile_ck.cmd` iki scripti derler. Paketli compile_headers yalnızca alternatif derleyici arayüzleridir; oyuna veya CK'nin gerçek script kaynakları üzerine kopyalanmamalıdır.

Makine tarafından okunabilir tam kayıt özeti: `CK_RECORDS.json`.

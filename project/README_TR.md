# Stamina On Hit - By Naens — 1.1.0

Skyrim Legendary Edition / Oldrim için yakın dövüş isabetlerinde stamina yenileme.
Oyuncu, takipçiler ve düşman NPC'ler desteklenir. Yenileme hedefe değil, vuran aktöre gider.

## Gereksinimler

- Skyrim LE / TESV 1.9.32.0 (32-bit).
- SKSE **1.7.3**; oyunu MO2 üzerinden SKSE ile başlat.
- MCM menüsü için **SkyUI 5.1 LE** ve onun scriptleri.
- SE/AE/VR sürümleri desteklenmez. SkyUI, SKSE veya oyun dosyaları bu pakette dağıtılmaz.

## Eski sürümden MO2 ile yükseltme

1. Oyunu tamamen kapat ve mevcut kaydının bir yedeğini al.
2. Bu ZIP'i MO2'de “Arşivden mod yükle” ile aç. Eski modun yerine **Replace / Değiştir** seçeneğiyle kur. MO2 yeni bir mod oluşturursa eski modu kapat; yalnızca yeni paket etkin olsun.
3. Sol panelde modun adını **Stamina On Hit - By Naens** olarak kullanabilirsin.
4. Sağ panelde **Nackufu_Stamina_on_Hit_LE.esp** etkin kalsın. ESP, DLL ve controller scriptinin eski teknik adları kayıtla bağlantıyı korumak için bilinçli olarak saklandı; bunları elle yeniden adlandırma.
5. SKSE ile açıp mevcut kaydını yükle. Yeni MCM kaydı için oyun içinde yaklaşık 30–60 saniye bekle.
6. **Esc → Mod Configuration → Stamina On Hit - By Naens → Settings** yolunu aç.

Eski ESP'yi kaldırıp arada modsuz kayıt oluşturma, quest'i durdurma veya kayıt temizleme işlemi bu yükseltmenin bir parçası değildir. Yalnızca yeni dosyalarla değiştir.
Yeni oyunda da aynı ZIP doğrudan kurulabilir. FOMOD, Data içeriğini doğru konuma yerleştirir; Developer klasörü kurulmaz.

## MCM seçenekleri

| Bölüm / seçenek | İşlev | Başlangıç değeri |
|---|---|---|
| PLAYER / Enable for player | Oyuncu yenilemesini aç/kapat | Açık |
| PLAYER / Stamina per hit | Oyuncunun isabet başına aldığı stamina | 10 |
| NPCs / Enable for NPCs | Takipçi ve düşmanların yenilemesini aç/kapat | Açık |
| NPCs / Stamina per hit | NPC'nin isabet başına aldığı stamina | 10 |

Miktarlar **0–100**, birer puanlık adımlarla seçilir. Sıfır, ilgili yenilemeyi durdurur. Ayarlar kayıt dosyasında saklanır; kayıt yüklemek bunları sıfırlamaz. MCM'nin varsayılana döndür tuşu seçili ayarı 10 veya açık konumuna getirir. Menü etiketleri standart SkyUI yazı tipleriyle çalışması için İngilizcedir.

## Hangi isabetler sayılır?

- Bir aktöre yapılan gerçek yakın dövüş silah isabetleri: hançer, kılıç, savaş baltası, topuz, büyük kılıç, iki elli balta/çekiç.
- Normal saldırılar, güçlü saldırılar ve hedefin blokladığı vuruşlar dahildir.
- Güçlü saldırının normal stamina maliyeti korunur; ayarlanan miktar ayrıca yenilenir.
- NPC → oyuncu ve NPC → NPC isabetleri NPC ayarını kullanır.
- Boşa savurma, bash/kalkan darbesi, yumruk/pençe, yay/arbalet, asa, büyü, mermi ve çevre nesnesine vurma dahil değildir.
- Büyülü silahın ek büyü bildirimleri ayrıca stamina vermez. Ayrı fiziksel isabetler ayrı ayrı sayılır.
- Maksimum stamina artırılmaz; mevcut stamina RestoreActorValue ile yenilenir.

## FNIS XXL ve diğer modlar

Bu paket animasyon, skeleton veya behavior dosyası içermez. Bu mod için FNIS çalıştırmak gerekmez. FNIS XXL iş akışına ek bir işlem getirmez.
Vanilla actor/race/weapon kayıtlarına override eklenmez; NPC dağıtım yaması veya çevredeki NPC'leri tarayan bir döngü kullanılmaz.
Aynı fiziksel isabet fonksiyonunu değiştiren başka bir DLL ile çakışma mümkündür. Bu sürüm yoğun NPC savaşlarında daha fazla Papyrus olayı üretir; ağır script yükünde yenileme gecikebilir.

## Menü veya etki görünmezse

- SkyUI **LE** scriptleri, yeni iki PEX, ESP ve DLL'nin MO2 sanal Data ağacında bulunduğunu kontrol et.
- Oyunu SKSE ile tamamen yeniden başlat; kayıt yükleyip MCM kaydına zaman tanı.
- Eski mod veya MO2 Overwrite içindeki eski NSH_PlayerAlias.pex/DLL yeni dosyaları ezmemeli.
- `Documents/My Games/Skyrim/SKSE/StaminaOnHitByNaens.log` içinde `ACTIVE` satırı aranır. `DISABLED` veya `REJECTED` satırı varsa gerekçe aynı günlükte yazılır.

## Doğrulama durumu

Önceki oyuncu odaklı sürüm kullanıcı tarafından oyunda çalışır olarak doğrulandı.
**Bu 1.1.0 güncellemesi Skyrim içinde henüz test edilmedi.** Derlenmiş x86 köprü emülasyonu, gerçek PEX bytecode testleri, bağımsız PEX decompile, ESP/VMAD/SEQ yapısı ve ZIP bütünlüğü kontrolleri yapıldı. Bunlar oyun içi MCM kaydı ve gerçek SKSE yüklemesinin yerine geçmez. Ayrıntılar `docs/VALIDATION.md`; kısa oyun testi `docs/TEST_PLANI_TR.md` içindedir.

ESP/PEX/DLL, Papyrus ve C kaynakları, CK kayıt açıklamaları, yeniden derleme araçları ve testler bu ZIP'e dahildir. `Developer/OriginalPrototype` yalnızca tarihsel kaynaktır; kurulmaz ve yeni sürümün çalışma yolu değildir.

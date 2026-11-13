# Oyun içi kabul testi — 1.1.0

Yedek kaydın üzerinde TESV 1.9.32 / SKSE 1.7.3 / SkyUI 5.1 LE / MO2 ile uygula.

1. Eski çalışan modun yerine yeni paketi kur, eski save'i yükle. Günlükte ACTIVE ve MCM'de doğru başlık görünmeli. Yeni oyunda da quest başlangıcını dene.
2. MCM'de oyuncu 23, NPC 7 seç. Stamina eksikken oyuncunun yakın dövüş isabeti +23 vermeli. Test sırasında normal stamina yenilenmesini hesaba kat; güçlü saldırının maliyetini yenilemeyle karıştırma.
3. Takipçinin düşmana, düşmanın oyuncuya ve iki NPC'nin birbirine vurmasını dene. Vuran NPC +7 almalı; hedef sırf vurulduğu için stamina almamalı. NPC stamina'sını konsolda aktörü seçip `getav stamina` ile izleyebilirsin.
4. Oyuncu anahtarını kapat: NPC çalışmaya devam etmeli. Sonra tersini dene. Miktar 0 da ilgili yenilemeyi durdurmalı.
5. Normal, bloklanan, güçlü ve bloklanan güçlü saldırıları dene. İki elli ve çift silahı da kontrol et. Boşa savurma, bash, yumruk, yay, büyü ve çevre nesnesine vurma yenilememeli.
6. Büyülü yakın dövüş silahıyla tek fiziksel isabette tek yenileme olmalı; büyü/hasar tikleri tekrar vermemeli. Art arda gerçek fiziksel isabetler ayrı sayılmalı.
7. MCM'nin varsayılana döndür tuşunu her dört ayarda dene. Değerler 10 ve açık olmalı. Slider 0–100 aralığında birer puan ilerlemeli.
8. Değerleri değiştir, normal kaydet, oyunu kapatıp aç. Aynı save yüklendiğinde değerler korunmalı; MCM ve isabetler çalışmalı.
9. Birkaç NPC içeren savaşta gecikme ve Papyrus hata günlüğünü gözle. Stamina, maksimum değerinin üstüne çıkmamalı.

Bu listedeki oyun testleri bu ortamda uygulanmadı. Otomatik kontrollerin kapsamı VALIDATION.md'de belirtilmiştir.

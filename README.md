# 🎯 Gelişmiş Terapili Dil Öğrenme Sistemi

Bu proje, yapay zeka destekli terapötik yaklaşımla dil öğrenmeyi birleştiren kapsamlı bir web uygulamasıdır. Kullanıcılar hem psikolojik destek alabilir hem de dil becerilerini geliştirebilirler.

## ✨ Yeni Özellikler (Güncellenmiş)

### 🎮 Gelişmiş Kelime Oyunu
- **Günlük Kelimeler**: Her gün yapay zeka tarafından üretilen yeni kelimeler
- **Zorluk Modu**: Seviyeye göre zorlaştırılmış kelimeler
- **Tekrar Modu**: Öğrenilen kelimelerin tekrarı
- **Çoklu Doğru Cevap**: Bir kelimenin birden fazla anlamı kabul edilir
- **Puan Sistemi**: Farklı oyun türlerine göre puan kazanma
- **Seviye İlerleme**: Görsel ilerleme çubukları

### 📊 Gelişmiş İlerleme Sistemi
- **Çoklu Kriter**: Sadece oyun puanları değil, chat ve günlük aktiviteleri de değerlendirilir
- **Zorlaştırılmış Seviye Atlama**: 
  - A1 → A2: 50 puan + 20 chat kelimesi + 10 günlük kelimesi
  - A2 → B1: 120 puan + 50 chat kelimesi + 25 günlük kelimesi
  - B1 → B2: 250 puan + 100 chat kelimesi + 50 günlük kelimesi
  - B2 → C1: 500 puan + 200 chat kelimesi + 100 günlük kelimesi

### 🤖 Yapay Zeka Entegrasyonu
- **Günlük Kelime Üretimi**: Gemini AI ile seviyeye uygun kelimeler
- **Akıllı Kelime Analizi**: Chat ve günlük yazılarından kelime çıkarımı
- **Dinamik İçerik**: Her gün farklı kelimeler ve içerikler

### 💬 Gelişmiş Chat Sistemi
- **Kelime Takibi**: Chat sırasında tespit edilen kelimeler ilerlemeye eklenir
- **Gerçek Zamanlı Analiz**: Her mesajda kelime sayısı gösterimi
- **Çoklu Dil Desteği**: 7 farklı dil seçeneği

### 📔 Akıllı Günlük Sistemi
- **Kelime Tespiti**: Yazılan metinlerden otomatik kelime çıkarımı
- **İlerleme Entegrasyonu**: Günlük kelimeleri seviye atlamaya katkı sağlar
- **Duygu Analizi**: Yazılan metinlerin duygu durumu analizi

## 🚀 Kurulum

### Gereksinimler
- Python 3.8+
- MySQL 8.0+
- Google Gemini API Key

### Adım 1: Veritabanı Kurulumu
```bash
# MySQL'de veritabanını oluşturun
mysql -u root -p < database_setup.sql
```

### Adım 2: Python Bağımlılıkları
```bash
pip install flask mysql-connector-python google-generativeai werkzeug
```

### Adım 3: Konfigürasyon
`app.py` dosyasında veritabanı bağlantı bilgilerini güncelleyin:
```python
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='your_password',
        database='proje_db'
    )
```

### Adım 4: API Key
`chatbot_logic.py` dosyasında Gemini API key'inizi ekleyin:
```python
configure(api_key="your_gemini_api_key")
```

### Adım 5: Uygulamayı Çalıştırın
```bash
python app.py
```

## 🎯 Kullanım

### 1. Kayıt ve Giriş
- Yeni kullanıcı kaydı oluşturun
- Dil seviyenizi ve öğrenmek istediğiniz dili seçin

### 2. Kelime Oyunu
- **Günlük Kelimeler**: Her gün yeni kelimeler öğrenin
- **Zorluk Modu**: Daha zorlu kelimelerle kendinizi test edin
- **Tekrar Modu**: Öğrendiğiniz kelimeleri pekiştirin

### 3. Chat Sistemi
- Farklı modlarda (aile, aşk, akademik, serbest) sohbet edin
- Her mesajınızda kelime sayısı takip edilir
- İlerlemeniz gerçek zamanlı olarak güncellenir

### 4. Günlük Yazma
- Günlük yazılarınızı paylaşın
- Otomatik kelime tespiti ve duygu analizi
- Chatbot yorumları alın

## 📊 İstatistikler ve İlerleme

### Seviye Sistemi
- **A1**: Başlangıç seviyesi
- **A2**: Temel seviye
- **B1**: Orta seviye
- **B2**: İleri seviye
- **C1**: Uzman seviye

### İlerleme Kriterleri
Her seviye için 3 farklı kriterin tamamlanması gerekir:
1. **Oyun Puanları**: Kelime oyunlarından kazanılan puanlar
2. **Chat Kelimeleri**: Sohbet sırasında kullanılan kelimeler
3. **Günlük Kelimeleri**: Günlük yazılarında tespit edilen kelimeler

## 🔧 Teknik Özellikler

### Backend
- **Flask**: Web framework
- **MySQL**: Veritabanı
- **Google Gemini**: Yapay zeka entegrasyonu
- **JSON**: Veri formatı

### Frontend
- **HTML5/CSS3**: Modern ve responsive tasarım
- **JavaScript**: Dinamik kullanıcı deneyimi
- **AJAX**: Gerçek zamanlı veri güncelleme

### Veritabanı Yapısı
- `users`: Kullanıcı bilgileri
- `chats`: Sohbet oturumları
- `chat_messages`: Sohbet mesajları
- `diary_entries`: Günlük yazıları
- `word_scores`: Kelime puanları
- `daily_words`: Günlük kelimeler
- `user_progress`: Kullanıcı ilerlemesi

## 🎨 Özellikler

### Çoklu Dil Desteği
- İngilizce, İspanyolca, Fransızca
- Korece, Japonca, Arapça
- Türkçe

### Responsive Tasarım
- Mobil uyumlu arayüz
- Modern ve kullanıcı dostu tasarım
- Animasyonlar ve görsel efektler

### Güvenlik
- Şifre hashleme
- Session yönetimi
- SQL injection koruması

## 🔮 Gelecek Özellikler

- [ ] Ses tanıma ve telaffuz kontrolü
- [ ] Video konferans entegrasyonu
- [ ] Sosyal öğrenme özellikleri
- [ ] Gamification elementleri
- [ ] Mobil uygulama
- [ ] Çoklu kullanıcı desteği

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Commit yapın (`git commit -m 'Add some AmazingFeature'`)
4. Push yapın (`git push origin feature/AmazingFeature`)
5. Pull Request oluşturun

## 📞 İletişim

Proje hakkında sorularınız için issue açabilirsiniz.

---

**Not**: Bu sistem hem dil öğrenme hem de psikolojik destek amaçlıdır. Ciddi psikolojik sorunlar için mutlaka profesyonel yardım alın.

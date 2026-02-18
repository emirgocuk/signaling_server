# QuickShare Signaling Server

Bu, QuickShare P2P dosya paylaşım uygulaması için güvenli ve özel "Signaling Server" (Sinyal Sunucusu) projesidir.

Bu sunucu, iki bilgisayarın birbirini bulmasını sağlar. Dosyalar BU SUNUCUDAN GEÇMEZ. Dosyalar doğrudan iki bilgisayar arasında (P2P) aktarılır. Bu sunucu sadece "Benim IP adresim şu" bilgisini taşır.

## Nasıl Deploy Edilir? (Ücretsiz)

### Yöntem 1: Render.com (Önerilen)

1.  Bu klasörü GitHub'a yeni bir repo olarak yükleyin (veya mevcut reponuzda tutun).
2.  [Render.com](https://render.com) hesabına giriş yapın.
3.  "New +" butonuna basın ve **"Web Service"** seçin.
4.  GitHub reponuzu bağlayın.
5.  Aşağıdaki ayarları yapın:
    *   **Name:** `quickshare-signal` (veya istediğiniz bir isim)
    *   **Runtime:** `Python 3`
    *   **Build Command:** `pip install -r requirements.txt`
    *   **Start Command:** `python server.py`
    *   **Free Instance Type:** Seçili olduğundan emin olun.
6.  "Create Web Service" butonuna tıklayın.
7.  Deploy bittiğinde size `https://quickshare-signal.onrender.com` gibi bir URL verecek.
8.  Bu URL'i kopyalayın ve QuickShare uygulamasındaki "Sinyal Sunucusu" ayarına yapıştırın.

### Yöntem 2: Glitch.com

1.  Glitch'te yeni proje oluşturun ("Import from GitHub").
2.  Bu dosyaları yükleyin.
3.  Zaten otomatik çalışacaktır.

## Güvenlik

*   Bu sunucu şeffaftır, veri tutmaz.
*   IP adreslerini sadece aynı ODA (Room) içindeki kişiler görebilir.
*   Güvenli bağlantı (HTTPS/WSS) kullanır.

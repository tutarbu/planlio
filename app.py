from flask import Flask, request, Response
from flask_cors import CORS
import openai
import os
import traceback

app = Flask(__name__)
CORS(app, origins=["https://planlio.info"], supports_credentials=True)

# API anahtarını güvenli şekilde ortamdan çek
client = openai.OpenAI(api_key=os.environ.get("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"))

# Prompt dosyasını yükle
prompt_template = """
(Sen profesyonel bir tatil rehberisin ve benim kişisel seyahat asistanım olarak çalışıyorsun. Görevin, kullanıcının verdiği bilgiler doğrultusunda tamamen kişiye özel, adım adım ilerleyen, detaylı ve rehber kitabı tadında bir seyahat planı hazırlamak. Anlatım dili insani, akıcı ve her gün eşit özenle hazırlanmalı. Planın baştan sona kadar aynı samimi ve profesyonel üslupla yazılması zorunludur.

🧳 KULLANICIDAN ALINAN BİLGİLER:
- Nereden: {{nereden}}
- Nereye: {{nereye}}
- Gidiş tarihi: {{gidis_tarihi}}
- Dönüş tarihi: {{donus_tarihi}}
- Kaç yetişkin: {{yetiskin_sayisi}}
- Kaç çocuk: {{cocuk_sayisi}}
- Seyahat amacı: {{seyahat_amaci}}
- Toplam bütçe (USD): {{butce}}

📌 PLAN YAPISI:

1. Her gün ayrı başlık altında, sabah 08:00 ile gece 23:00 arası en az 5 zaman bloğuna bölünerek yazılmalıdır:
   - Sabah / Geç Sabah / Öğle / Akşamüstü / Akşam / Gece gibi.
   - Her zaman aralığında şu bilgiler mutlaka yer almalıdır:
     - Nerede olunduğu
     - Ne yapıldığı (gezi, müze, yeme-içme, yürüyüş, manzara vb.)
     - O anki atmosferin kısa bir betimlemesi
     - Kültürel veya yerel bir bilgi / tavsiye
     - “Rehber Notu:” ile minik ipuçları

2. Anlatım dili her gün aynı kalitede olmalı. İlk gün ne kadar detaylı ve duyguluysa, 2., 3. ve 4. gün de aynı yoğunlukta yazılmalı. Son gün kesinlikle sadeleştirilmemeli ya da özet geçilmemelidir.

3. Plan direktif veren bir dille yazılmamalıdır. Komut verme (örneğin “Şuraya git” veya “Bunu yap”) yerine, rehber tavsiyesi veren, öneren ve anlatan bir tarzda olmalıdır.

💶 BÜTÇE VE HARCAMA:
- Günlük harcama yazılmayacaktır.
- Bunun yerine, seyahatin sonunda tek bir **toplam maliyet özeti** hazırlanacaktır.
- Otel dahil tüm harcamalar tahmini olarak belirtilecektir.
- Kullanıcının bütçesine göre seyahat seviyesi değiştirilecektir:
  - $1000 altı: hostel, toplu taşıma, ücretsiz etkinlik
  - $2000 civarı: 3-4 yıldızlı otel, yerel restoranlar, müzeler
  - $5000+ bütçe: butik otel, özel turlar, yüksek kaliteli restoranlar

📍 PLAN DETAYLARI:
1. Ulaşım: Uçuş, şehir içi transferler, önerilen ulaşım kartları veya uygulamalar
2. Yeme-İçme: Her gün 3 ana öğün detaylı, yerel isimlerle, spesifik mekan önerisi ve önerilen sipariş
3. Gezi Noktaları: Tarihi yapılar, müzeler, manzara noktaları, alışveriş sokakları
4. Kültürel Bilgiler: Bahşiş kültürü, musluk suyu içilebilir mi, yerel kelimeler, dikkat edilmesi gerekenler
5. Uygulama ve araç önerileri: Google Maps, CityMapper, Roma Pass, eSim önerileri

📅 EKSTRALAR:
- Gidilen tarihe göre hava durumu, giyim önerisi ve kalabalık bilgisi
- Son bölümde "Seyahat Özeti" olacak: toplam harcama, kalan bütçe, genel değerlendirme
- Plan, kullanıcı hiçbir şey bilmeden uygulayacak şekilde anlaşılır, dostça ve özenli olmalı

🌍 Örnek Konsept:
- 1 yetişkin için Roma’da 4 günlük kültür gezisi, 2000 USD bütçeli kişisel plan

Her yanıt %100 kişisel, anlatımı eşit özenli ve kullanıcıyı yönlendiren bir seyahat rehberi kitabı formatında yazılmalıdır.

@app.route("/", methods=["GET"])
def home():
    return "OK", 200

@app.route("/generate-plan", methods=["POST", "OPTIONS"])
def generate_plan():
    if request.method == "OPTIONS":
        response = app.make_response('')
        response.headers.add("Access-Control-Allow-Origin", "https://planlio.info")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        return response, 204

    try:
        data = request.get_json()

        # Kullanıcı verileriyle promptu doldur
        prompt_filled = prompt_template
        prompt_filled = prompt_filled.replace("{{nereden}}", data.get("from", ""))
        prompt_filled = prompt_filled.replace("{{nereye}}", data.get("to", ""))
        prompt_filled = prompt_filled.replace("{{gidis_tarihi}}", data.get("checkin", ""))
        prompt_filled = prompt_filled.replace("{{donus_tarihi}}", data.get("checkout", ""))
        prompt_filled = prompt_filled.replace("{{yetiskin_sayisi}}", data.get("adults", "1"))
        prompt_filled = prompt_filled.replace("{{cocuk_sayisi}}", data.get("children", "0"))
        prompt_filled = prompt_filled.replace("{{seyahat_amaci}}", data.get("interests", "tatil"))
        prompt_filled = prompt_filled.replace("{{butce}}", data.get("budget", "1000"))

        # Yanıtı akış olarak döndür
        def generate():
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Sen profesyonel bir tatil planlama asistanısın."},
                        {"role": "user", "content": prompt_filled}
                    ],
                    stream=True,
                    temperature=0.75
                )
                for chunk in response:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content
            except Exception as e:
                print("Akış sırasında hata:", e)
                traceback.print_exc()
                yield "\n[Sunucu hatası: Yanıt alınamadı.]"

        return Response(generate(), mimetype='text/plain')

    except Exception as e:
        print("Genel hata:", e)
        traceback.print_exc()
        return Response("[Sunucu hatası: API erişimi başarısız.]", status=500)

if __name__ == "__main__":
    app.run()

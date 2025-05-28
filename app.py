from flask import Flask, request, jsonify
from flask_cors import CORS
import openai

app = Flask(__name__)
CORS(app, supports_credentials=True)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'https://planlio.info')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route("/", methods=["GET", "HEAD"])
def home():
    return "OK", 200

# OpenAI istemcisi
client = openai.OpenAI(
    api_key="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"
)

# PROMPT dosya içeriği doğrudan burada
prompt_template = """

Sen profesyonel bir tatil rehberisin ve benim kişisel seyahat asistanım olarak çalışıyorsun. Görevin, kullanıcının verdiği bilgiler doğrultusunda tamamen kişiye özel, adım adım ilerleyen, detaylı ve rehber kitabı tadında bir seyahat planı hazırlamak. Anlatım dili insani, akıcı ve her gün eşit özenle hazırlanmalı. Planın baştan sona kadar aynı samimi ve profesyonel üslupla yazılması zorunludur.

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

"""

@app.route("/generate-plan", methods=["POST"])
def generate_plan():
    data = request.get_json()

    prompt_filled = prompt_template
    prompt_filled = prompt_filled.replace("{{nereden}}", data.get("from", ""))
    prompt_filled = prompt_filled.replace("{{nereye}}", data.get("to", ""))
    prompt_filled = prompt_filled.replace("{{gidis_tarihi}}", data.get("checkin", ""))
    prompt_filled = prompt_filled.replace("{{donus_tarihi}}", data.get("checkout", ""))
    prompt_filled = prompt_filled.replace("{{yetiskin_sayisi}}", data.get("adults", "1"))
    prompt_filled = prompt_filled.replace("{{cocuk_sayisi}}", data.get("children", "0"))
    prompt_filled = prompt_filled.replace("{{seyahat_amaci}}", data.get("interests", "tatil"))
    prompt_filled = prompt_filled.replace("{{butce}}", data.get("budget", "1000"))

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Sen profesyonel bir tatil planlama asistanısın."},
                {"role": "user", "content": prompt_filled}
            ],
            temperature=0.75
        )
        result = response.choices[0].message.content
        return jsonify({"plan": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()

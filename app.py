from flask import Flask, request, jsonify
from flask_cors import CORS
import openai

app = Flask(__name__)
CORS(app, origins=["https://planlio.info", "https://www.planlio.info"])  # Sadece kendi domain'ine izin verir

@app.route("/", methods=["GET", "HEAD"])
def home():
    return "OK", 200

# OpenAI istemcisi
client = openai.OpenAI(api_key="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")

# Prompt şablonu doğrudan gömülü
prompt_template = """
Sen kişiye özel tatil planlamada uzman bir seyahat danışmanısın. Kullanıcının gideceği şehir, tarih, konaklayacağı süre, kişi sayısı ve bütçesi gibi bilgileri dikkate alarak ona unutulmaz bir seyahat planı oluşturmalısın. Lütfen yanıtını aşağıdaki örneğe benzer, günlük olarak ayrılmış bir plan şeklinde ve samimi bir dille ver.

📌 Seyahat Özeti:
- Nereden: {{nereden}}
- Nereye: {{nereye}}
- Gidiş Tarihi: {{gidis_tarihi}}
- Dönüş Tarihi: {{donus_tarihi}}
- Süre: Toplam gün sayısını belirt (örn: 4 gece 5 gün)
- Yetişkin Sayısı: {{yetiskin_sayisi}}
- Çocuk Sayısı: {{cocuk_sayisi}}
- Seyahat Amacı: {{seyahat_amaci}}
- Toplam Bütçe: {{butce}} USD
- Tahmini Kişi Başı Günlük Harcama: yaklaşık belirt
- Mevsim Bilgisi: Gideceği tarihteki tipik hava durumu ve öneri kıyafetler
- Konaklama Önerisi: Şehir merkezine yakın, bütçeye uygun bir otel önerisi

📅 Günlük Plan:
Her gün için sabah, öğle, akşam aktivitelerini öner:
- Gezilecek yerler (tarihi, kültürel, doğal)
- Yerel yemek önerileri (mekan adı + yöresel tatlar)
- Yerel deneyimler (pazar, müze, yürüyüş rotası, sokaklar)
- Ulaşım notları (toplu taşıma, yürüme mesafesi)
- Yerel ipuçları ve dikkat edilmesi gerekenler

Planı, kullanıcıya hitap eder gibi yaz ve eğlenceli emojilerle süsle 🎒📷🍽️
"""

@app.route("/generate-plan", methods=["POST", "OPTIONS"])
def generate_plan():
    if request.method == "OPTIONS":
        return '', 200  # Preflight CORS isteği

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
            model="gpt-4.5-preview",
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
    app.run(debug=True)

from flask import Flask, request, jsonify
from flask_cors import CORS
import openai

app = Flask(__name__)
CORS(app, supports_credentials=True)

@app.route("/", methods=["GET", "HEAD"])
def home():
    return "OK", 200

# OpenAI istemcisi
client = openai.OpenAI(api_key="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")

# Prompt metni doğrudan gömülü
prompt_template = """Merhaba! Artık senin kişisel tatil planlama asistanınım 🧳✈️

Lütfen bana aşağıdaki bilgileri sağlayarak seyahat tercihlerini belirt:
- Nereden seyahat edeceksin?
- Nereye gitmek istiyorsun?
- Gidiş tarihi ve dönüş tarihi nedir?
- Kaç yetişkin ve kaç çocuk seyahat edecek?
- Seyahat amacın ne? (Kültürel gezi, deniz tatili, gastronomi, alışveriş, doğa, eğlence vb.)
- Seyahat bütçen nedir?

Senin verdiğin bilgilere göre en uygun, detaylı ve kişiselleştirilmiş bir seyahat planı oluşturacağım. ☀️🌍

📌 Not: Seyahat tarihine göre hava durumunu ve kalabalık durumunu da dikkate alırım. Aynı zamanda kültürel etkinlikleri, yerel lezzetleri, çocuklu seyahatlerde uygunluğu da göz önünde bulundururum.

Verdiğin bilgilere göre şu yapıda bir plan sunacağım:
- Genel Tanıtım
- Günlük Plan (Her gün için sabah, öğle, akşam aktiviteleri ve yemek önerileri)
- Otel ve konaklama önerileri
- Ulaşım ve yol tarifleri
- Ekstra öneriler (Gizli kalmış yerler, ipuçları vs)

Şimdi lütfen aşağıdaki bilgileri gir:
- Nereden: {{nereden}}
- Nereye: {{nereye}}
- Gidiş Tarihi: {{gidis_tarihi}}
- Dönüş Tarihi: {{donus_tarihi}}
- Yetişkin Sayısı: {{yetiskin_sayisi}}
- Çocuk Sayısı: {{cocuk_sayisi}}
- Seyahat Amacı: {{seyahat_amaci}}
- Bütçe: {{butce}} USD

Hazırsan başlayalım! 🚀"""

@app.route("/generate-plan", methods=["POST", "OPTIONS"])
def generate_plan():
    if request.method == "OPTIONS":
        return '', 200

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

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
import os
import traceback

app = Flask(__name__)
CORS(app, origins=["https://planlio.info"], supports_credentials=True)

# Gemini 2.0 Flash model endpoint (v1beta!)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

# Basitleştirilmiş ve hızlı prompt
prompt_template = """
Sen bir seyahat danışmanısın. Aşağıdaki bilgilerle kişisel bir tatil planı hazırla:

- Nereden: {{nereden}}
- Nereye: {{nereye}}
- Gidiş: {{gidis_tarihi}} – Dönüş: {{donus_tarihi}}
- Yetişkin: {{yetiskin_sayisi}} – Çocuk: {{cocuk_sayisi}}
- Amaç: {{seyahat_amaci}} – Bütçe: {{butce}} USD

Her gün sabah, öğle, akşam bölümlerine ayrılmış, öneri içeren sade bir plan yaz.
"Kullanıcının seyahat edeceği şehir için otel ve uçuş rezervasyonu yapması gerekiyorsa, Trip.com'a yönlendiren şu bağlantıyı öner: https://trip.tp.st/ylMdsQmX. 'Trip.com üzerinden rezervasyon yap' gibi sade bir cümle ile geçir."
"""

@app.route("/", methods=["GET"])
def home():
    return "OK", 200

@app.route("/generate-plan", methods=["POST", "OPTIONS"])
def generate_plan():
    if request.method == "OPTIONS":
        response = Response()
        response.headers["Access-Control-Allow-Origin"] = "https://planlio.info"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response, 204

    try:
        data = request.get_json()
        print("👉 Alınan veri:", data)

        prompt = prompt_template
        prompt = prompt.replace("{{nereden}}", data.get("from", ""))
        prompt = prompt.replace("{{nereye}}", data.get("to", ""))
        prompt = prompt.replace("{{gidis_tarihi}}", data.get("checkin", ""))
        prompt = prompt.replace("{{donus_tarihi}}", data.get("checkout", ""))
        prompt = prompt.replace("{{yetiskin_sayisi}}", data.get("adults", "1"))
        prompt = prompt.replace("{{cocuk_sayisi}}", data.get("children", "0"))
        prompt = prompt.replace("{{seyahat_amaci}}", data.get("interests", "tatil"))
        prompt = prompt.replace("{{butce}}", data.get("budget", "1000"))

        print("📤 Prompt:", prompt[:300], "...")

        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }

        response = requests.post(GEMINI_URL, headers=headers, json=payload)
        result = response.json()

        print("📥 Gemini cevabı:", result)

        if "candidates" in result:
            content = result["candidates"][0]["content"]["parts"][0]["text"]
            return jsonify({"plan": content})
        else:
            return jsonify({"error": result.get("error", "Yanıt alınamadı.")}), 500

    except Exception as e:
        print("❌ HATA:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()

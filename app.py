from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
import os
import traceback

app = Flask(__name__)
CORS(app, origins=["https://planlio.info"], supports_credentials=True)

GEMINI_API_KEY = os.environ.get("AIzaSyD6XWUjxQ9chZrmI0G7DhwGMSrVEgpCd-s")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro-latest:generateContent?key={GEMINI_API_KEY}"

# Prompt şablonu (kısa, güçlü)
prompt_template = """
Sen deneyimli bir tatil danışmanısın. Kullanıcıdan alınan bilgilerle kişiye özel bir seyahat planı oluştur.

Plan; gün gün sabah, öğle, akşam bölümlerinden oluşsun. Her bölümde gidilecek yer, yapılacak aktivite, kısa açıklama ve yerel tavsiyeler ver.

Anlatım doğal, rehber diliyle yazılsın. Komut verici değil, açıklayıcı ve akıcı olsun.

Plan sonunda toplam maliyet özeti yer alsın. Bütçeye uygunluk, ulaşım, yemek, kültürel bilgiler ve yerel öneriler de dahil edilsin.

Bilgiler:
- Nereden: {{nereden}}
- Nereye: {{nereye}}
- Gidiş: {{gidis_tarihi}} – Dönüş: {{donus_tarihi}}
- Yetişkin: {{yetiskin_sayisi}} – Çocuk: {{cocuk_sayisi}}
- Amaç: {{seyahat_amaci}} – Bütçe: {{butce}} USD
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
        print("👉 Alınan form verisi:", data)

        prompt = prompt_template
        prompt = prompt.replace("{{nereden}}", data.get("from", ""))
        prompt = prompt.replace("{{nereye}}", data.get("to", ""))
        prompt = prompt.replace("{{gidis_tarihi}}", data.get("checkin", ""))
        prompt = prompt.replace("{{donus_tarihi}}", data.get("checkout", ""))
        prompt = prompt.replace("{{yetiskin_sayisi}}", data.get("adults", "1"))
        prompt = prompt.replace("{{cocuk_sayisi}}", data.get("children", "0"))
        prompt = prompt.replace("{{seyahat_amaci}}", data.get("interests", "tatil"))
        prompt = prompt.replace("{{butce}}", data.get("budget", "1000"))

        print("🧠 Oluşan prompt:", prompt[:500], "...")

        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }

        print("📤 Gönderilen payload:", payload)

        response = requests.post(GEMINI_URL, headers=headers, json=payload)
        result = response.json()

        print("📥 Gemini yanıtı:", result)

        if "candidates" in result:
            content = result["candidates"][0]["content"]["parts"][0]["text"]
            return jsonify({"plan": content})
        else:
            return jsonify({"error": result.get("error", "Gemini cevabı alınamadı.")}), 500

    except Exception as e:
        print("❌ HATA:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()

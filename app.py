from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app, origins=["https://planlio.info"], supports_credentials=True)

GEMINI_API_KEY = os.environ.get("AIzaSyD6XWUjxQ9chZrmI0G7DhwGMSrVEgpCd-s")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro-latest:generateContent?key={GEMINI_API_KEY}"

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

@app.route("/generate-plan", methods=["POST"])
def generate_plan():
    try:
        data = request.get_json()

        prompt = prompt_template
        prompt = prompt.replace("{{nereden}}", data.get("from", ""))
        prompt = prompt.replace("{{nereye}}", data.get("to", ""))
        prompt = prompt.replace("{{gidis_tarihi}}", data.get("checkin", ""))
        prompt = prompt.replace("{{donus_tarihi}}", data.get("checkout", ""))
        prompt = prompt.replace("{{yetiskin_sayisi}}", data.get("adults", "1"))
        prompt = prompt.replace("{{cocuk_sayisi}}", data.get("children", "0"))
        prompt = prompt.replace("{{seyahat_amaci}}", data.get("interests", "tatil"))
        prompt = prompt.replace("{{butce}}", data.get("budget", "1000"))

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

        response = requests.post(GEMINI_URL, headers=headers, json=payload)
        result = response.json()

        if "candidates" in result:
            content = result["candidates"][0]["content"]["parts"][0]["text"]
            return jsonify({"plan": content})
        else:
            return jsonify({"error": result.get("error", "Bilinmeyen hata")}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()

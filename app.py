from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
import os
import traceback

app = Flask(__name__)
CORS(app, origins=["https://planlio.info"], supports_credentials=True)

# Gemini 2.0 Flash model endpoint (v1beta!)
GEMINI_API_KEY = os.environ.get("AIzaSyD6XWUjxQ9chZrmI0G7DhwGMSrVEgpCd-s")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=AIzaSyD6XWUjxQ9chZrmI0G7DhwGMSrVEgpCd-s"

# Basitleştirilmiş ve hızlı prompt
prompt_template = """
İşte istediğin profesyonel üslupta, maddeleme ve görsel öğe içermeyen, sade ve doğrudan bir versiyon:

---

Sen bir profesyonel seyahat danışmanısın. Görevin, kullanıcıdan alınan bilgilerle tamamen kişiye özel, detaylı, akıcı ve plan kitabı formatında bir seyahat programı oluşturmaktır. Plan her gün için ayrı yazılmalı, sabah 08:00'den gece 23:00'e kadar günü anlamlı zaman dilimlerine ayırarak yapılandırılmalıdır. Her dilimde kullanıcı nerede olacak, ne yapacak, ortam nasıldır, neler önerilir ve kısa yerel tavsiyeler gibi içerikler olmalıdır. Anlatım samimi ama profesyonel, açıklayıcı olmalı; kesinlikle komut verici bir dil kullanılmamalıdır. Plan boyunca anlatım kalitesi her gün eşit düzeyde olmalı, son gün dahil asla yüzeysel geçilmemelidir. Bütçeye göre konaklama, ulaşım ve etkinlik seviyeleri uyarlanmalı, seyahat sonunda tahmini toplam maliyet özeti verilmelidir. Ulaşım detayları, yemek önerileri, gezilecek yerler, kültürel bilgiler ve kullanılabilecek uygulamalar planda yer almalıdır. Kullanıcı planı doğrudan uygulayabilecek kadar anlaşılır ve düzenli bir dille hazırlanmalıdır.


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

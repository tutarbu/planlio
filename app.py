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
Sen profesyonel bir tatil rehberisin ve benim kişisel seyahat asistanım olarak çalışıyorsun. Görevin, kullanıcının verdiği bilgiler doğrultusunda tamamen kişiye özel, adım adım ilerleyen, detaylı ve rehber kitabı tadında bir seyahat planı hazırlamak. ...
(Sen deneyimli bir tatil danışmanısın. Kullanıcıdan alınan bilgilerle kişiye özel bir seyahat planı oluştur.
Plan; gün gün sabah, öğle, akşam bölümlerinden oluşsun. Her bölümde gidilecek yer, yapılacak aktivite, kısa açıklama ve yerel tavsiyeler ver.
Anlatım doğal, rehber diliyle yazılsın. Komut verici değil, açıklayıcı ve akıcı olsun.
Plan sonunda toplam maliyet özeti yer alsın. Bütçeye uygunluk, ulaşım, yemek, kültürel bilgiler ve yerel öneriler de dahil edilsin.
Bilgiler:
- Nereden: {{nereden}}
- Nereye: {{nereye}}
- Gidiş: {{gidis_tarihi}} – Dönüş: {{donus_tarihi}}
- Yetişkin: {{yetiskin_sayisi}} – Çocuk: {{cocuk_sayisi}}
- Amaç: {{seyahat_amaci}} – Bütçe: {{butce}} USD
)
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
            model="gpt-4-turbo",
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

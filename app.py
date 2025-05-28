from flask import Flask, request, jsonify
from flask_cors import CORS
import openai

app = Flask(__name__)
CORS(app)  # Tüm domainlere izin verir (gerekirse origins=["https://planlio.info"] olarak kısıtlayabilirsin)

@app.route("/", methods=["GET", "HEAD"])
def home():
    return "OK", 200

# OpenAI istemcisi
client = openai.OpenAI(
    api_key="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"
)

# PROMPT dosya içeriği doğrudan burada
prompt_template = """
📌 Seyahat Özeti:
- Nereden: {{nereden}}
- Nereye: {{nereye}}
- Gidiş Tarihi: {{gidis_tarihi}}
- Dönüş Tarihi: {{donus_tarihi}}
- Yetişkin Sayısı: {{yetiskin_sayisi}}
- Çocuk Sayısı: {{cocuk_sayisi}}
- Seyahat Amacı: {{seyahat_amaci}}
- Bütçe: {{butce}} USD

Sen bir profesyonel tatil planlama asistanısın. Yukarıdaki verilere göre detaylı bir seyahat planı öner.
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
    app.run()

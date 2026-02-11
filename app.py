import os
from flask import Flask, request
import telebot
import google.generativeai as genai
import requests
from PIL import Image
from io import BytesIO

# Configurazione
TOKEN_SENSOR = os.getenv("TOKEN_SENSOR")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
# Sostituisci la riga del bot con questa per un debug migliore
TOKEN_SENSOR = os.getenv("TOKEN_SENSOR")
if not TOKEN_SENSOR:
    print("ERRORE: Variabile TOKEN_SENSOR non trovata!")
bot = telebot.TeleBot(TOKEN_SENSOR)

app = Flask(__name__)

SYSTEM_PROMPT = "Agisci come SENSOR. Estrai dati, identifica pattern e descrivi oggettivamente ciò che vedi, sia in testo che in immagini."

@app.route('/webhook/sensor', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    return 'Forbidden', 403

@bot.message_handler(content_types=['text'])
def handle_text(message):
    response = model.generate_content(f"{SYSTEM_PROMPT}\n\nAnalizza: {message.text}")
    bot.reply_to(message, f"📡 [SENSOR DATA]:\n\n{response.text}")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{TOKEN_SENSOR}/{file_info.file_path}"
    img_response = requests.get(file_url)
    img = Image.open(BytesIO(img_response.content))
    
    prompt = message.caption if message.caption else "Analizza questa immagine."
    response = model.generate_content([f"{SYSTEM_PROMPT}\n{prompt}", img])
    bot.reply_to(message, f"👁️ [SENSOR VISION]:\n\n{response.text}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

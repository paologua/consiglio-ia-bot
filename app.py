import os
import telebot
import google.generativeai as genai
from flask import Flask, request

# Configurazione
TOKEN = os.getenv("TOKEN_SENSOR")
API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=API_KEY)
# Usiamo il modello più stabile
model = genai.GenerativeModel('gemini-1.5-flash')

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/webhook/sensor', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return 'OK', 200

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # 1. Messaggio di log su Railway
        print(f"Ricevuto messaggio: {message.text}")
        
        # 2. Generazione risposta con Gemini
        response = model.generate_content(message.text)
        
        # 3. Invio risposta
        bot.reply_to(message, response.text)
        
    except Exception as e:
        # Se c'è un errore, il bot te lo scriverà su Telegram!
        error_msg = f"❌ Errore Sensor: {str(e)}"
        print(error_msg)
        bot.reply_to(message, error_msg)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

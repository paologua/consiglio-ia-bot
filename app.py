import os
import telebot
import google.generativeai as genai
from flask import Flask, request

# 1. RECUPERO VARIABILI D'AMBIENTE
# Assicurati che su Railway siano scritte esattamente così
TOKEN = os.getenv("TOKEN_SENSOR")
API_KEY = os.getenv("GEMINI_API_KEY")

# 2. CONFIGURAZIONE GOOGLE AI
genai.configure(api_key=API_KEY)
# Utilizziamo 'gemini-pro' per evitare l'errore 404 del modello flash
model = genai.GenerativeModel('gemini-pro')

# 3. INIZIALIZZAZIONE BOT E SERVER
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# 4. ROTTA PER IL WEBHOOK
@app.route('/webhook/sensor', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    else:
        return 'Error', 403

# 5. GESTIONE MESSAGGI
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # Log di controllo nei Deploy Logs di Railway
        print(f"📡 Sensor riceve: {message.text}")
        
        # Generazione della risposta con l'IA
        response = model.generate_content(
            f"Agisci come il 'Sensor' del Consiglio IA. Analizza brevemente questo input: {message.text}"
        )
        
        # Invio risposta al bot
        bot.reply_to(message, f"📡 [SENSOR DATA]:\n\n{response.text}")
        
    except Exception as e:
        # Se c'è un errore, lo scrive sia nei log che a te su Telegram
        error_details = f"❌ Errore Sensor: {str(e)}"
        print(error_details)
        bot.reply_to(message, error_details)

# 6. AVVIO SERVER
if __name__ == "__main__":
    # Railway assegna automaticamente una porta, noi la leggiamo
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

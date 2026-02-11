import os
import telebot
import google.generativeai as genai
from flask import Flask, request

# 1. CONFIGURAZIONE VARIABILI
TOKEN = os.getenv("TOKEN_SENSOR")
API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=API_KEY)

# 2. INIZIALIZZAZIONE
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# 3. LOGICA DI GENERAZIONE (Con prova modelli multipli)
def generate_response(user_text):
    # Lista dei nomi modelli dal più recente al più stabile
    model_names = [
        'gemini-1.5-flash-latest', 
        'gemini-1.5-flash', 
        'gemini-pro', 
        'gemini-1.0-pro'
    ]
    
    for name in model_names:
        try:
            print(f"Tentativo con modello: {name}")
            model = genai.GenerativeModel(name)
            response = model.generate_content(
                f"Agisci come il 'Sensor' del Consiglio IA. Analizza: {user_text}"
            )
            return response.text
        except Exception as e:
            print(f"Modello {name} fallito: {e}")
            continue # Passa al prossimo modello nella lista
            
    return "❌ Nessun modello Gemini disponibile. Controlla i permessi della API Key."

# 4. ROTTA WEBHOOK
@app.route('/webhook/sensor', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    return 'Error', 403

# 5. GESTORE MESSAGGI TELEGRAM
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    print(f"📡 Messaggio ricevuto: {message.text}")
    bot.send_chat_action(message.chat.id, 'typing')
    
    testo_risposta = generate_response(message.text)
    bot.reply_to(message, f"📡 [SENSOR DATA]:\n\n{testo_risposta}")

# 6. AVVIO
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

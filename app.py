import os
import telebot
import requests
from flask import Flask, request

# CONFIGURAZIONE
TOKEN = os.getenv("TOKEN_SENSOR")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

def ask_groq(question):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    # Usiamo il modello più stabile di Groq
    data = {
        "model": "llama-3.3-70b-versatile", 
        "messages": [
            {"role": "system", "content": "Sei il Sensor del Consiglio IA. Fornisci analisi brevi."},
            {"role": "user", "content": question}
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        res_json = response.json()
        
        if 'choices' in res_json:
            return res_json['choices'][0]['message']['content']
        else:
            # Questo ci dirà il vero errore di Groq (es. API key invalida)
            error_info = res_json.get('error', {}).get('message', 'Errore sconosciuto')
            return f"Dettaglio Errore Groq: {error_info}"
    except Exception as e:
        return f"Errore Connessione: {str(e)}"

@app.route('/webhook/sensor', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    return 'Error', 403

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.send_chat_action(message.chat.id, 'typing')
    risposta = ask_groq(message.text)
    bot.reply_to(message, f"📡 [SENSOR DATA]:\n\n{risposta}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

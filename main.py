import os
import telebot
from google import genai
from google.genai import types

# 1. CONFIGURACIÓN DE LLAVES (Mantén tus claves reales aquí dentro)
TELEGRAM_TOKEN = "8939512104:AAHl2lZI6_tS8dJPANtCaDHA7eSamOxor1Y"
GEMINI_API_KEY = "AQ.Ab8RN6KwATPjhhe47ltci5Qhryai-wa4qbrPM5RE-YeUguRDkg"

# 2. INICIALIZACIÓN
bot = telebot.TeleBot(TELEGRAM_TOKEN)
ai_client = genai.Client(api_key=GEMINI_API_KEY)

user_chats = {}

# 3. CONTENIDO DEL LIBRO (Pega aquí el texto que copiaste de tu Lección 3)
TEXTO_LECCION = """
[PEGA AQUÍ TODO EL TEXTO DE LA LECCIÓN 3 QUE COPIASTE DE TU LIBRO]
"""

SYSTEM_PROMPT = f"""
Eres un tutor interactivo de inglés americano basado estrictamente en el siguiente contenido del libro:
{TEXTO_LECCION}

Tu objetivo es enseñar al usuario a hablar inglés mediante diálogos cortos y dinámicos (estilo chat).
REGLAS OBLIGATORIAS:
1. Inicia saludando en inglés de forma amigable y propón el primer diálogo corto basado en la Lección 3.
2. Ve paso a paso. No envíes explicaciones largas. Envía una sola línea de diálogo a la vez.
3. Incluye siempre la pronunciación figurada (entre paréntesis o cursiva) y la traducción al español abajo para ayudar al usuario.
4. Si el usuario comete un error al responder, corrígelo amablemente antes de continuar el diálogo.
"""

def get_or_create_chat(user_id):
    if user_id not in user_chats:
        chat = ai_client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7,
            )
        )
        user_chats[user_id] = chat
    return user_chats[user_id]

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if user_id in user_chats:
        del user_chats[user_id]
    chat = get_or_create_chat(user_id)
    ai_response = chat.send_message("Hola, inicia el diálogo interactivo de la lección desde el principio.")
    bot.reply_to(message, ai_response.text)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    chat = get_or_create_chat(user_id)
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        ai_response = chat.send_message(message.text)
        bot.reply_to(message, ai_response.text)
    except Exception as e:
        bot.reply_to(message, "¡Disculpa! Tuve un pequeño parpadeo de conexión. ¿Podrías repetir tu último mensaje?")
        print(f"Error: {e}")

# Servidor web ultra-simple para mantener feliz a Render Free
if __name__ == "__main__":
    from threading import Thread
    from http.server import HTTPServer, BaseHTTPRequestHandler
    class SimpleHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot OK")
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    Thread(target=server.serve_forever, daemon=True).start()
    
    bot.infinity_polling()

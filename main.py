import os
import telebot
from g4f.client import Client

# 1. CONFIGURACIÓN DE TELEGRAM (Coloca tu token real de BotFather aquí dentro)
TELEGRAM_TOKEN = "8939512104:AAHl2lZI6_tS8dJPANtCaDHA7eSamOxor1Y"

# 2. INICIALIZACIÓN
bot = telebot.TeleBot(TELEGRAM_TOKEN)
ai_client = Client()

# 3. CONTENIDO DEL LIBRO
TEXTO_LECCION = """
Lección 3. LAS PRIMERAS PALABRAS
Es momento de aprender las palabras, frases y expresiones más frecuentes usadas en el inglés. Las cuales te ayudarán a expresarte cotidianamente.

ESPAÑOL | INGLÉS | PRONUNCIACIÓN
sí | yes | iés
no | no | no
quizás | maybe | méibi
yo soy (estoy) | I am | ái em
yo tengo | I have | ái jav
es (está) | It is | it is
nada | nothing | názing
todo | everything | évrizing
nunca | never | nevár
siempre | always | ólueis
quiero | I want | ái uónt
no quiero | I don't want | ái don't uónt
me gustaría | I would like | ái úud like
aquí | here | jiar
allá | there | zéar
hoy | today | tudéi
ayer | yesterday | iésterdei
mañana | tomorrow | tumórrou
pasado mañana | the day after tomorrow | zé déi áftar tumórrou
bueno | good | gúud
esto aquí | this one | dis uán
ese allá | that one | dat uán
un momento | just a second | chyast e sécond
antes | before | bifóar
después | after | áftár
a menudo | often | óften
raras veces | seldom | séldom
una vez | once | uáns
muchas veces | many times | méni táims
otra vez | again | eguéin
con | with | uiz
sin | without | uizáut
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

# Historial de mensajes para que la IA recuerde la conversación
user_histories = {}

def get_ai_response(user_id, user_message):
    if user_id not in user_histories:
        user_histories[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    user_histories[user_id].append({"role": "user", "content": user_message})
    
    # Llamada al proveedor libre de Inteligencia Artificial
    response = ai_client.chat.completions.create(
        model="gpt-4o",
        messages=user_histories[user_id]
    )
    
    ai_text = response.choices[0].message.content
    user_histories[user_id].append({"role": "assistant", "content": ai_text})
    return ai_text

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if user_id in user_histories:
        del user_histories[user_id]
    
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        reply = get_ai_response(user_id, "Hola, inicia el diálogo interactivo de la lección desde el principio.")
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, "Iniciando tutor... Por favor envía /start nuevamente en 5 segundos.")
        print(f"Error: {e}")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        reply = get_ai_response(user_id, message.text)
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, "Tuve un pequeño problema al procesar el mensaje. ¿Podrías repetirlo?")
        print(f"Error: {e}")

# Servidor web para Render Free
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

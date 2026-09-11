import os
import telebot
import google.generativeai as genai

# 1. CONFIGURACIÓN DE LLAVES (Coloca tus llaves reales aquí dentro)
TELEGRAM_TOKEN = "8939512104:AAHl2lZI6_tS8dJPANtCaDHA7eSamOxor1Y"
GEMINI_API_KEY = "AQ.Ab8RN6KwATPjhhe47ltci5Qhryai-wa4qbrPM5RE-YeUguRDkg"

# 2. INICIALIZACIÓN COMPATIBLE
bot = telebot.TeleBot(TELEGRAM_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)

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

# Configuración del modelo clásico
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_PROMPT
)

user_chats = {}

def get_or_create_chat(user_id):
    if user_id not in user_chats:
        user_chats[user_id] = model.start_chat(history=[])
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
        bot.reply_to(message, f"¡Disculpa! Tuve un pequeño parpadeo de conexión. ¿Podrías repetir tu último mensaje?")
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

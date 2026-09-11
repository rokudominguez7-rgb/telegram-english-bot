import os
import telebot
from google import genai
from google.genai import types

# 1. CONFIGURACIÓN DE LLAVES (Reemplaza con tus datos reales)
TELEGRAM_TOKEN = "8939512104:AAHl2lZI6_tS8dJPANtCaDHA7eSamOxor1Y"
GEMINI_API_KEY = "AQ.Ab8RN6KwATPjhhe47ltci5Qhryai-wa4qbrPM5RE-YeUguRDkg"

# 2. INICIALIZACIÓN DE CLIENTES
bot = telebot.TeleBot(TELEGRAM_TOKEN)
ai_client = genai.Client(api_key=GEMINI_API_KEY)

# Diccionario temporal para guardar el historial de chat de cada usuario
user_chats = {}

print("Subiendo libro a Gemini... Por favor espera.")
# Subimos el PDF a la API de Gemini para que sirva de contexto permanente
book_file = ai_client.files.upload(file="libro.pdf")
print("¡Libro cargado con éxito! Bot encendido y listo.")

# Instrucciones del sistema para la IA (System Instruction)
SYSTEM_PROMPT = """
Eres un tutor interactivo de inglés americano basado estrictamente en el libro provisto.
Tu objetivo es enseñar al usuario a hablar inglés mediante diálogos cortos y dinámicos (estilo chat).
REGLAS:
1. Inicia saludando en inglés de forma amigable y propón un diálogo corto basado en la Lección 3.
2. Ve paso a paso. No envíes textos largos. Envía una o dos líneas de diálogo a la vez.
3. Incluye siempre la pronunciación figurada (entre paréntesis o cursiva) y la traducción al español abajo para ayudar al usuario, tal como lo hace el método del libro.
4. Si el usuario comete un error al responder, corrígelo amablemente antes de continuar el diálogo.
5. Mantén un tono entusiasta y motivador.
"""

def get_or_create_chat(user_id):
    """Crea o recupera la sesión de chat con IA para un usuario específico."""
    if user_id not in user_chats:
        # Iniciamos un chat con el modelo optimizado y pasamos el archivo del libro como contexto
        chat = ai_client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7,
            ),
            history=[
                types.Content(
                    role="user",
                    parts=[book_file, types.Part.from_text("Hola, quiero empezar a aprender inglés con el método del libro.")]
                )
            ]
        )
        user_chats[user_id] = chat
    return user_chats[user_id]

# Manejador del comando /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    # Forzamos el reinicio de la conversación si ya existía
    if user_id in user_chats:
        del user_chats[user_id]
        
    chat = get_or_create_chat(user_id)
    # Enviamos el primer mensaje generado por la IA (el saludo inicial)
    ai_response = chat.send_message("Empieza la lección interactiva desde el principio.")
    bot.reply_to(message, ai_response.text)

# Manejador para cualquier mensaje de texto que envíe el usuario
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    chat = get_or_create_chat(user_id)
    
    # Mostramos un estado de "escribiendo..." en Telegram para mejorar la experiencia
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        # Enviamos la respuesta del usuario a la IA y obtenemos la réplica del tutor
        ai_response = chat.send_message(message.text)
        bot.reply_to(message, ai_response.text)
    except Exception as e:
        bot.reply_to(message, "Ups, hubo un pequeño problema técnico al procesar tu mensaje. ¡Inténtalo de nuevo!")
        print(f"Error: {e}")

# Inicia el bot en modo escucha continua
bot.infinity_polling()

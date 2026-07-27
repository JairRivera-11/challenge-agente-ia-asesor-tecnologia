from dotenv import load_dotenv

load_dotenv()

from app.services.llm import generate

historial = [
    {"role": "user", "content": "hola, busco una notebook"},
    {"role": "assistant", "content": "¡Hola! ¿Para qué la vas a usar y qué presupuesto manejás?"},
]

print(generate("para programar, hasta 900 dolares", history=historial))
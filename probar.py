from dotenv import load_dotenv

load_dotenv()

from app.services.search import buscar

print(buscar("precio RTX 5070 Argentina 2026"))
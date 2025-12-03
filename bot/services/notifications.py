import httpx
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

async def update_subscription(telegram_id: int, action: str):
    url = f"{BACKEND_URL}/notifications/subscribe" if action == "on" else f"{BACKEND_URL}/notifications/unsubscribe"
    payload = {"telegram_id": str(telegram_id)}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        if response.status_code not in (200, 201):
            raise Exception(f"Erro ao atualizar inscrição: {response.text}")
        return response.json()

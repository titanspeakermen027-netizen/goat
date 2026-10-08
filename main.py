import json
import time
import asyncio
import os
import websockets
from dotenv import load_dotenv

# تحميل المتغيرات من ملف .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    print("[-] خطأ: لم يتم العثور على التوكن في ملف .env!")
    exit(1)

# رابط WebSocket حق ديسكورد
discord_ws_url = "wss://gateway.discord.gg/?v=9&encoding=json"

async def run_spotify_rpc():
    payload = {
        "op": 2,
        "d": {
            "token": TOKEN,
            "properties": {
                "$os": "windows",
                "$browser": "Discord Client",
                "$device": "desktop"
            },
            "presence": {
                "activities": [{
                    "name": "Spotify",
                    "type": 2, # 2 تعني Listening
                    "details": "Moonlight",
                    "state": "by XXXTENTACION",
                    "timestamps": {
                        "start": int(time.time()),
                        "end": int(time.time()) + 135 # مدة أغنية Moonlight
                    },
                    "assets": {
                        "large_image": "spotify:ab67616d0000b27380f2d81a951a750a2e3a89a0",
                        "large_text": "17"
                    },
                    "flags": 48,
                    "party": {
                        "id": "spotify:685324483789062225"
                    },
                    "sync_id": "0JP9xo3adEtGDCUEIBihDL",
                    "session_id": "1234567890abcdef1234567890abcdef"
                }],
                "status": "online",
                "since": 0,
                "afk": False
            }
        }
    }

    try:
        async with websockets.connect(discord_ws_url) as websocket:
            print("[+] تم الاتصال بـ Discord بنجاح باستخدام ملف .env!")
            await websocket.send(json.dumps(payload))
            
            # حلقة تكرار عشان يبقى الاتصال شغال والحالة مثبتة
            while True:
                await asyncio.sleep(45)
                heartbeat = {"op": 1, "d": None}
                await websocket.send(json.dumps(heartbeat))
                
    except Exception as e:
        print(f"[-] حدث خطأ: {e}")

if __name__ == "__main__":
    asyncio.run(run_spotify_rpc())

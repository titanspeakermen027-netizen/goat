import os
import asyncio
import discord
from dotenv import load_dotenv

# تحميل المتغيرات من ملف .env
load_dotenv()

# جلب التوكن من ملف .env
TOKEN = os.getenv("DISCORD_TOKEN")

# اسم اللعبة
GAME_NAME = "Ƙinɣdøm Of Aphamia  🏰"

# رابط الصورة التي أرفقتها (بعد رفعها على موقع مثل Imgur وضعي رابطها المباشر)
# يمكنك وضع رابط صورة مباشر (يبدأ بـ https:// وينتهي بـ .jpg أو .png)
IMAGE_URL = "https://images-ext-1.discordapp.net/external/9BnrFcgAy-5tAi0-SbVovH7C8hJkp3XeaWP2Feh-uAw/https/cdn.discordapp.com/icons/1412468404954337423/b8e95eae828bcf31cfbdb91e7ea0cabc.webp" 

class MyClient(discord.Client):
    async def on_ready(self):
        print(f"تم تسجيل الدخول بنجاح باسم: {self.user}")
        
        # إعداد حالة اللعب (Activity)
        activity = discord.Activity(
            type=discord.ActivityType.playing, # نوع النشاط: يمارس لعبة (Playing)
            name=GAME_NAME,                    # اسم اللعبة
            details="Playing Ƙinɣdøm Of Aphamia", # التفاصيل الفرعية
            state="In Game 🏰",                # الحالة الفرعية
            assets={
                "large_image": IMAGE_URL,      # رابط الصورة الكبيرة
                "large_text": GAME_NAME        # النص الذي يظهر عند وضع الماوس على الصورة
            }
        )
        
        # تطبيق الحالة على الحساب
        await self.change_presence(activity=activity)
        print(f"تم تفعيل حالة اللعب: {GAME_NAME}")

client = MyClient()

if TOKEN:
    client.run(TOKEN)
else:
    print("خطأ: لم يتم العثور على التوكن في ملف .env")

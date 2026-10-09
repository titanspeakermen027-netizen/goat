import os
import asyncio
import discord
from discord.ext import tasks
from dotenv import load_dotenv

# تحميل المتغيرات من ملف .env
load_dotenv()

# جلب التوكن من ملف .env بأمان
TOKEN = os.getenv("DISCORD_TOKEN")

# آيدي الروم الذي تريد إظهار حالة الكتابة فيه
CHANNEL_ID = 1538885237159891054

class MyClient(discord.Client):
    async def setup_hook(self):
        self.keep_typing.start()

    async def on_ready(self):
        print(f"تم تسجيل الدخول بنجاح باسم: {self.user}")

    @tasks.loop(seconds=5.0)
    async def keep_typing(self):
        channel = self.get_channel(CHANNEL_ID)
        if channel:
            try:
                # إرسال إشارة الكتابة بشكل مستمر
                async with channel.typing():
                    await asyncio.sleep(5)
            except Exception as e:
                print(f"حدث خطأ أثناء الكتابة: {e}")

    @keep_typing.before_loop
    async def before_keep_typing(self):
        await self.wait_until_ready()

client = MyClient()

if TOKEN:
    client.run(TOKEN, bot=False)
else:
    print("خطأ: لم يتم العثور على التوكن في ملف .env")

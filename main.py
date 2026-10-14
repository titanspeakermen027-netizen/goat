import os
import discord
from dotenv import load_dotenv

# تحميل البيانات من ملف .env
load_dotenv()

# قراءة التوكن من متغيرات البيئة
TOKEN = os.getenv("DISCORD_TOKEN")

client = discord.Client()

@client.event
async def on_ready():
    print(f"تم تسجيل الدخول بنجاح باسم: {client.user}")

@client.event
async def on_raw_reaction_add(payload):
    # يتجاهل التفاعلات الصادرة من حسابك لتجنب التكرار
    if payload.user_id == client.user.id:
        return

    try:
        # جلب القناة والرسالة
        channel = await client.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        
        # إضافة نفس الرياكشن
        await message.add_reaction(payload.emoji)
        print(f"تمت إضافة الرياكشن {payload.emoji} على الرسالة: {message.id}")
        
    except Exception as e:
        print(f"حدث خطأ أثناء إضافة الرياكشن: {e}")

# التحقق من وجود التوكن قبل التشغيل
if not TOKEN:
    print("خطأ: لم يتم العثور على DISCORD_TOKEN في ملف .env")
else:
    client.run(TOKEN)

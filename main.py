import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# تحميل البيانات من ملف .env
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

# إنشاء كائن السيلف بوت
bot = commands.Bot(command_prefix="!", self_bot=True)

@bot.event
async def on_ready():
    print(f"==========================================")
    print(f"تم تسجيل الدخول بنجاح باسم: {bot.user}")
    print(f"==========================================")

    # إعداد الـ Rich Presence بالمعلومات المطلوبة
    activity = discord.Activity(
        type=discord.ActivityType.playing,
        name="Ƙinɣdøm Of Aphamia  🏰",
        application_id=1558946040806117457,  # آيدي التطبيق الخاص بك
        details="In Kingdom",                  # النص الأول تحت اسم اللعبة
        state="Exploring the realm...",        # النص الثاني
        assets={
            "large_image": "logo",             # اسم مفتاح الصورة الذي رفعتها في Developer Portal
            "large_text": "Ƙinɣdøm Of Aphamia  🏰" # النص الذي يظهر عند وضع الماوس على الصورة
        }
    )

    # تطبيق النشاط وتحديث الحالة إلى Online
    await bot.change_presence(activity=activity, status=discord.Status.online)
    print("تم تفعيل حالة اللعبة والصورة بنجاح!")

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("خطأ: لم يتم العثور على DISCORD_TOKEN داخل ملف .env")

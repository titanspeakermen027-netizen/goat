import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="!", self_bot=True)

@bot.event
async def on_ready():
    print(f"تم تسجيل الدخول بنجاح باسم: {bot.user}")

    # رابط صورة اللعبة المرفق
    IMAGE_URL = "https://images-ext-1.discordapp.net/external/9BnrFcgAy-5tAi0-SbVovH7C8hJkp3XeaWP2Feh-uAw/https/cdn.discordapp.com/icons/1412468404954337423/b8e95eae828bcf31cfbdb91e7ea0cabc.webp"

    # إنشاء النشاط وتحديد الاسم والصورة
    activity = discord.Activity(
        type=discord.ActivityType.playing,
        name="Ƙinɣdøm Of Aphamia  🏰",
        details="In Kingdom",  # النص الذي يظهر تحت اسم اللعبة (اختياري)
        state="Exploring the realm...",  # النص الفرعي الثاني (اختياري)
        assets={
            "large_image": IMAGE_URL,
            "large_text": "Ƙinɣdøm Of Aphamia"  # النص عند التمرير على الصورة
        }
    )

    # تطبيق الحالة (أونلاين + النشاط)
    await bot.change_presence(activity=activity, status=discord.Status.online)
    print("تم تفعيل حالة اللعبة الوهمية والصورة بنجاح!")

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("خطأ: لم يتم العثور على التوكين في ملف .env")

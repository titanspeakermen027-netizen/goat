import json
import os
import discord
from dotenv import load_dotenv

# تحميل المتغيرات من ملف .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

TARGET_CHANNEL_ID = 1538885237159891054
COUNTER_FILE = "message_counter.json"

intents = discord.Intents.default()
intents.message_content = True  # مفيد لقراءة محتوى الرسائل

client = discord.Client(intents=intents)

def load_counter():
    """تحميل العداد السابق من الملف لتفادي فقدان التقدم عند إعادة التشغيل"""
    if os.path.exists(COUNTER_FILE):
        try:
            with open(COUNTER_FILE, "r") as f:
                data = json.load(f)
                return data.get("count", 0)
        except Exception:
            return 0
    return 0

def save_counter(count):
    """حفظ العداد الحالي في الملف"""
    with open(COUNTER_FILE, "w") as f:
        json.dump({"count": count}, f)

message_count = load_counter()

@client.event
async def on_ready():
    print(f"تم تسجيل الدخول بنجاح باسم: {client.user}")
    print(f"العداد الحالي للرسائل المرسلة: {message_count}")
    print(f"مراقبة القناة المستهدفة: {TARGET_CHANNEL_ID}")

@client.event
async def on_message(message):
    global message_count

    # التأكد من أن الرسالة صدرت منك شخصياً وفي القناة المستهدفة فقط
    if message.author.id == client.user.id and message.channel.id == TARGET_CHANNEL_ID:
        
        # تجاهل الرسالة إذا كانت هي النقطة التي أرسلها الحساب بنفسه لكي لا تحسب ضمن العداد
        if message.content == ".":
            return

        message_count += 1
        save_counter(message_count)
        
        print(f"تم إرسال رسالة جديدة. العدد الحالي: {message_count}")

        # التحقق مما إذا كان العدد قد وصل إلى مضاعفات الـ 100
        if message_count % 100 == 0:
            try:
                await message.channel.send(".")
                print(f"تم إرسال نقطة (.) بعد بلوغ {message_count} رسالة.")
            except Exception as e:
                print(f"حدث خطأ أثناء إرسال النقطة: {e}")

# تشغيل البوت باستخدام التوكن المستورد من ملف .env
if TOKEN:
    client.run(TOKEN)
else:
    print("خطأ: لم يتم العثور على التوكن في ملف .env")

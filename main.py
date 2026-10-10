import os
import sqlite3
import requests
from cryptography.fernet import Fernet
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

SECRET_KEY = Fernet.generate_key()
cipher_suite = Fernet(SECRET_KEY)

db = sqlite3.connect("quest_data.db")
cursor = db.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_configs (
        user_id TEXT PRIMARY KEY,
        encrypted_token TEXT,
        selected_quest TEXT,
        selected_country TEXT
    )
""")
db.commit()

intents = discord.Intents.default()
intents.messages = True
intents.dm_messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

# دالة لجلب الكويستات الحقيقية من حساب المستخدم عبر توكنه
def fetch_user_quests(raw_token: str):
    headers = {
        "Authorization": raw_token,
        "Content-Type": "application/json"
    }
    try:
        # جلب المهام المتاحة لحساب ديسكورد
        response = requests.get("https://discord.com/api/v9/users/@me/quests", headers=headers)
        if response.status_code == 200:
            data = response.json()
            quests = data.get("quests", [])
            
            options = []
            for quest in quests:
                quest_id = quest.get("id")
                config = quest.get("config", {})
                title = config.get("messages", {}).get("quest_name", "مهمة ديسكورد")
                
                # التحقق مما إذا كانت المهمة مكتملة أو لا
                user_status = quest.get("user_status", {})
                completed = user_status.get("completed", False)
                
                status_emoji = "✅" if completed else "🔒"
                desc = "مكتملة" if completed else "غير مكتملة (متاحة للإنجاز)"
                
                options.append(
                    discord.SelectOption(
                        label=title[:100],
                        description=desc,
                        value=str(quest_id),
                        emoji=status_emoji
                    )
                )
            
            # إذا لم يتم العثور على كويستات نشطة
            if not options:
                options.append(discord.SelectOption(label="لا توجد كويستات متاحة حالياً", value="none", emoji="❌"))
                
            return options[:25] # ديسكورد يسمح بحد أقصى 25 خياراً في القائمة
        else:
            return None
    except Exception as e:
        print(f"Error fetching quests: {e}")
        return None

class QuestControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="عرض المهمة", style=discord.ButtonStyle.link, url="https://discord.com"))

    @discord.ui.button(label="إيقاف", style=discord.ButtonStyle.secondary, emoji="🟣")
    async def stop_quest(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🛑 تم إيقاف المهمة.", ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.secondary, emoji="🔄")
    async def refresh_quest(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔄 جاري تحديث بيانات المهمة...", ephemeral=True)

class DynamicQuestSelectView(discord.ui.View):
    def __init__(self, user_id: str, encrypted_token: str, quest_options: list):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.encrypted_token = encrypted_token
        
        # إضافة قائمة الكويستات التي تم جلبها تلقائياً من حساب المستخدم
        self.quest_select = discord.ui.Select(
            placeholder="اختر الكويست من حسابك...",
            options=quest_options
        )
        self.quest_select.callback = self.select_quest_callback
        self.add_item(self.quest_select)

    async def select_quest_callback(self, interaction: discord.Interaction):
        selected_quest = self.quest_select.values[0]
        if selected_quest == "none":
            await interaction.response.send_message("❌ لا توجد مهام صالحة للاختيار.", ephemeral=True)
            return

        cursor.execute(
            "INSERT OR REPLACE INTO user_configs (user_id, encrypted_token, selected_quest) VALUES (?, ?, ?)",
            (self.user_id, self.encrypted_token, selected_quest)
        )
        db.commit()

        await interaction.response.send_message(
            f"✅ **تم اختيار المهمة بنجاح!**\n"
            f"🎯 معرف المهمة: `{selected_quest}`\n"
            f"⚙️ جاري بدء تشغيل السكريبت لإنجازها...",
            ephemeral=True
        )

@bot.tree.command(name="badge", description="جلب كويستات حسابك وتحديدها تلقائياً")
@app_commands.describe(access="أدخل توكن حسابك هنا للربط المشفّر")
async def badge_command(interaction: discord.Interaction, access: str):
    if interaction.guild_id is not None:
        await interaction.response.send_message(
            "❌ هذا الأمر يعمل فقط في **الخاص (Direct Messages)** لحماية توكن حسابك!",
            ephemeral=True
        )
        return

    # جلب الكويستات الحقيقية عبر التوكن المدخل
    quest_options = fetch_user_quests(access)
    if quest_options is None:
        await interaction.response.send_message("❌ فشل الاتصال بحسابك. تأكد من صحة التوكن المدخل.", ephemeral=True)
        return

    # تشفير التوكن بعد التحقق منه وصناعته
    encrypted_token = cipher_suite.encrypt(access.encode('utf-8')).decode('utf-8')
    user_id = str(interaction.user.id)

    embed = discord.Embed(
        title="🔐 تم جلب مهام حسابك بنجاح",
        description="تم فحص حسابك ومعرفة المهام المكتملة وغير المكتملة. اختر الكويست الذي تريد إنجازه من القائمة أدناه:",
        color=discord.Color.green()
    )

    view = DynamicQuestSelectView(user_id=user_id, encrypted_token=encrypted_token, quest_options=quest_options)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ البوت يعمل الآن باسم: {bot.user}")

bot.run(TOKEN)

import os
import sqlite3
from cryptography.fernet import Fernet
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

# تحميل المتغيرات من ملف .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# إعداد نظام التشفير وقاعدة البيانات
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

# أزرار التحكم أسفل بطاقة المهمة
class QuestControlView(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=None)

  @discord.ui.button(
      label="إيقاف", style=discord.ButtonStyle.secondary, emoji="🟣"
  )
  async def stop_quest(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    await interaction.response.send_message("🛑 تم إيقاف المهمة.", ephemeral=True)

  @discord.ui.button(style=discord.ButtonStyle.secondary, emoji="🔄")
  async def refresh_quest(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    await interaction.response.send_message(
        "🔄 جاري تحديث بيانات المهمة...", ephemeral=True
    )

  @discord.ui.button(
      label="عرض المهمة",
      style=discord.ButtonStyle.link,
      url="https://discord.com",
  )
  async def view_quest(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    pass


# واجهة اختيار الكويست والدولة في الخاص
class QuestSetupView(discord.ui.View):

  def __init__(self, user_id: str, encrypted_token: str):
    super().__init__(timeout=180)
    self.user_id = user_id
    self.encrypted_token = encrypted_token
    self.quest = None
    self.country = None

  @discord.ui.select(
      placeholder="🎮 اختر الكويست الذي تريد إكماله...",
      options=[
          discord.SelectOption(
              label="VALORANT", value="valorant", emoji="⚔️"
          ),
          discord.SelectOption(
              label="Genshin Impact", value="genshin", emoji="✨"
          ),
          discord.SelectOption(label="Fortnite", value="fortnite", emoji="🏆"),
      ],
  )
  async def select_quest(
      self, interaction: discord.Interaction, select: discord.ui.Select
  ):
    self.quest = select.values[0]
    await interaction.response.send_message(
        f"✅ تم تحديد الكويست: **{self.quest.upper()}**", ephemeral=True
    )
    await self.check_and_save(interaction)

  @discord.ui.select(
      placeholder="🌍 اختر الدولة / السيرفر...",
      options=[
          discord.SelectOption(
              label="السعودية (SA)", value="SA", emoji="🇸🇦"
          ),
          discord.SelectOption(label="الإمارات (AE)", value="AE", emoji="🇦🇪"),
          discord.SelectOption(label="مصر (EG)", value="EG", emoji="🇪🇬"),
          discord.SelectOption(label="البرازيل (BR)", value="BR", emoji="🇧🇷"),
          discord.SelectOption(
              label="الولايات المتحدة (US)", value="US", emoji="🇺🇸"
          ),
      ],
  )
  async def select_country(
      self, interaction: discord.Interaction, select: discord.ui.Select
  ):
    self.country = select.values[0]
    await interaction.response.send_message(
        f"✅ تم تحديد الدولة: **{self.country}**", ephemeral=True
    )
    await self.check_and_save(interaction)

  async def check_and_save(self, interaction: discord.Interaction):
    if self.quest and self.country:
      cursor.execute(
          "INSERT OR REPLACE INTO user_configs (user_id, encrypted_token,"
          " selected_quest, selected_country) VALUES (?, ?, ?, ?)",
          (self.user_id, self.encrypted_token, self.quest, self.country),
      )
      db.commit()

      # بناء بطاقة المحاكاة المطابقة للصور بعد اكتمال الاختيار
      embed = discord.Embed(color=discord.Color.from_rgb(88, 101, 242))
      embed.add_field(
          name="الجوائز:",
          value=(
              "• **Champions Shanghai: Frag or Die Avatar Decoration**\n  ⏱️"
              " أشهر 2 لمدة 🟣"
          ),
          inline=False,
      )
      tasks_text = (
          "• العب على الكمبيوتر لمدة 15 دقيقة 💻\n• العب على Xbox لمدة 15 دقيقة"
          " 🎮\n• العب على PlayStation لمدة 15 دقيقة 🎮"
      )
      embed.add_field(name="المهام:", value=tasks_text, inline=False)
      embed.add_field(
          name="اسم اللعبة:", value=self.quest.upper(), inline=False
      )
      embed.add_field(name="الناشر:", value="Riot Games", inline=False)
      embed.add_field(
          name="اسم المهمة:", value=f"Play {self.quest.upper()}", inline=False
      )
      embed.add_field(
          name="تاريخ التسجيل:", value="10/10/2026 2:54 PM", inline=False
      )
      embed.add_field(name="تنتهي في:", value="10/19/2026 1:00 AM", inline=False)
      embed.add_field(
          name="التقدم:", value="💻 0%\n🎮 0%\n🎮 0%", inline=False
      )
      embed.set_footer(
          text=f"{self.quest.capitalize()} | 10/05/2026 6:00 PM - الدولة:"
          f" {self.country}"
      )

      log_embed = discord.Embed(color=discord.Color.from_rgb(47, 49, 54))
      log_text = (
          "```text\n==================================================\n[1]"
          f" [INFO] Play {self.quest.upper()}: تم التسجيل في المهمة\n[2]"
          " [INFO] بدأ برنامج الحل العمل.\n[3] [INFO] 0/900 :تقدم المهمة\n```"
      )
      log_embed.add_field(name="السجلات", value=log_text, inline=False)

      await interaction.followup.send(
          content="🚀 **تم بدء تنفيذ السكريبت وحل المهمة بنجاح!**",
          embeds=[embed, log_embed],
          view=QuestControlView(),
          ephemeral=True,
      )


# أمر /badge في الخاص
@bot.tree.command(
    name="badge", description="ربط حسابك وتحديد الكويست والدولة لإكمال المهام"
)
@app_commands.describe(access="أدخل توكن حسابك هنا للربط المشفّر")
async def badge_command(interaction: discord.Interaction, access: str):
  if interaction.guild_id is not None:
    await interaction.response.send_message(
        "❌ هذا الأمر يعمل فقط في **الخاص (Direct Messages)** لحماية توكن"
        " حسابك!",
        ephemeral=True,
    )
    return

  encrypted_token = cipher_suite.encrypt(access.encode("utf-8")).decode(
      "utf-8"
  )
  user_id = str(interaction.user.id)

  embed = discord.Embed(
      title="🔐 تم تشفير التوكن بنجاح",
      description=(
          "اختر **الكويست** و **الدولة** من القوائم أدناه لكي يبدأ البوت في"
          " التنفيذ:"
      ),
      color=discord.Color.green(),
  )
  embed.add_field(
      name="🔒 التوكن المشفر",
      value=f"`{encrypted_token[:20]}...ENCRYPTED`",
      inline=False,
  )

  view = QuestSetupView(user_id=user_id, encrypted_token=encrypted_token)
  await interaction.response.send_message(
      embed=embed, view=view, ephemeral=True
  )


@bot.event
async def on_ready():
  await bot.tree.sync()
  print(f"✅ البوت يعمل الآن باسم: {bot.user}")


# تشغيل البوت باستخدام التوكن المحفوظ في ملف .env
bot.run(TOKEN)

import discord
from discord.ext import commands

# استخدام مكتبة Self-bot
client = commands.Bot(command_prefix="!", self_bot=True)

@client.event
async def on_ready():
    print(f"Logged in successfully as: {client.user} (ID: {client.user.id})")
    print("--------------------------------------------------")
    print("جاهز لعملية الاستنساخ! اكتب الأمر داخل أي سيرفر تملك صلاحيات فيه:")
    print("!clone <source_guild_id> <target_guild_id>")

@client.command(name="clone")
async def clone_server(ctx, source_guild_id: int, target_guild_id: int):
    await ctx.message.delete()
    
    source_guild = client.get_guild(source_guild_id)
    destination_guild = client.get_guild(target_guild_id)

    if not source_guild:
        await ctx.send("❌ لم أتمكن من العثور على السيرفر المراد نسخه. تأكد أن حسابك موجود فيه!", delete_after=10)
        return

    if not destination_guild:
        await ctx.send("❌ لم أتمكن من العثور على السيرفر الجديد. تأكد أن حسابك موجود فيه ولديك صلاحيات الإدارة!", delete_after=10)
        return

    status_msg = await ctx.send(f"🔄 جاري بدء استنساخ سيرفر **{source_guild.name}** إلى **{destination_guild.name}**...")

    # 1. تنظيف السيرفر الجديد من الرومات والرتب القديمة (اختياري)
    for channel in destination_guild.channels:
        try:
            await channel.delete()
        except Exception:
            pass

    for role in destination_guild.roles:
        if role != destination_guild.default_role and not role.managed:
            try:
                await role.delete()
            except Exception:
                pass

    # 2. نسخ الرتب بترتيب تنازلي
    role_mapping = {}
    sorted_roles = sorted(source_guild.roles, key=lambda r: r.position, reverse=True)
    
    for role in sorted_roles:
        if role == source_guild.default_role:
            role_mapping[role] = destination_guild.default_role
            try:
                await destination_guild.default_role.edit(
                    permissions=role.permissions,
                    color=role.color,
                    hoist=role.hoist,
                    mentionable=role.mentionable
                )
            except Exception:
                pass
            continue

        if role.managed:
            continue

        try:
            new_role = await destination_guild.create_role(
                name=role.name,
                permissions=role.permissions,
                color=role.color,
                hoist=role.hoist,
                mentionable=role.mentionable
            )
            role_mapping[role] = new_role
        except Exception as e:
            print(f"Failed to create role {role.name}: {e}")

    # 3. نسخ الفئات والرومات
    for category in source_guild.categories:
        try:
            overwrites = {}
            for target, perm in category.overwrites.items():
                if isinstance(target, discord.Role) and target in role_mapping:
                    overwrites[role_mapping[target]] = perm

            new_cat = await destination_guild.create_category(
                name=category.name,
                overwrites=overwrites,
                position=category.position
            )

            for channel in category.channels:
                ch_overwrites = {}
                for target, perm in channel.overwrites.items():
                    if isinstance(target, discord.Role) and target in role_mapping:
                        ch_overwrites[role_mapping[target]] = perm

                if isinstance(channel, discord.TextChannel):
                    await destination_guild.create_text_channel(
                        name=channel.name,
                        category=new_cat,
                        topic=channel.topic,
                        slowmode_delay=channel.slowmode_delay,
                        nsfw=channel.nsfw,
                        overwrites=ch_overwrites
                    )
                elif isinstance(channel, discord.VoiceChannel):
                    await destination_guild.create_voice_channel(
                        name=channel.name,
                        category=new_cat,
                        bitrate=channel.bitrate,
                        user_limit=channel.user_limit,
                        overwrites=ch_overwrites
                    )
        except Exception as e:
            print(f"Failed to clone category {category.name}: {e}")

    # 4. نسخ الرومات التي خارج الفئات
    for channel in source_guild.channels:
        if channel.category is None:
            try:
                ch_overwrites = {}
                for target, perm in channel.overwrites.items():
                    if isinstance(target, discord.Role) and target in role_mapping:
                        ch_overwrites[role_mapping[target]] = perm

                if isinstance(channel, discord.TextChannel):
                    await destination_guild.create_text_channel(
                        name=channel.name,
                        topic=channel.topic,
                        slowmode_delay=channel.slowmode_delay,
                        nsfw=channel.nsfw,
                        overwrites=ch_overwrites
                    )
                elif isinstance(channel, discord.VoiceChannel):
                    await destination_guild.create_voice_channel(
                        name=channel.name,
                        bitrate=channel.bitrate,
                        user_limit=channel.user_limit,
                        overwrites=ch_overwrites
                    )
            except Exception as e:
                print(f"Failed to clone channel {channel.name}: {e}")

    await status_msg.edit(content="✅ تم الانتهاء من استنساخ السيرفر بنجاح عبر حسابك الشخصي!")

# ضع توكن حسابك هنا (ملاحظة: لا تشاركه مع أي شخص أبداً)
TOKEN = input("أدخل توكن حسابك الشخصي هنا: ")
client.run(TOKEN, bot=False)

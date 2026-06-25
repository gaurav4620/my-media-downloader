import os
import asyncio
from pyrogram import Client, filters, idle
from pyrogram.errors import UserNotParticipant, ChatAdminRequired, PeerIdInvalid
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from yt_dlp import YoutubeDL

# ---- CONFIGURATION ----
API_ID = 20060680          # Apni API ID dalein (Integer me)
API_HASH = "fb7e080bc19d911c14f758b39605febc" # Apna API HASH dalein
BOT_TOKEN = "8709264133:AAFbUFYU1dgOuLaynhitaRHZRP1Tt9UxiEE" # Apna Bot Token dalein

BOT_USERNAME = "SheinFrsh_bot"        # Aapke bot ka sahi username (Bina '@' ke)
CHANNEL_USERNAME = "offerfactorynew"    # Aapke channel ka username (Bina '@' ke)
GROUP_USERNAME = "AllcontentNew"        # Aapke group ka username (Bina '@' ke)
# -----------------------

app = Client("MediaDownloaderBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Force join check karne ka function
async def is_user_joined(client, user_id):
    if CHANNEL_USERNAME == "your_channel" or GROUP_USERNAME == "your_group":
        return True
    try:
        await client.get_chat_member(CHANNEL_USERNAME, user_id)
        await client.get_chat_member(GROUP_USERNAME, user_id)
        return True
    except UserNotParticipant:
        return False
    except Exception as e:
        print(f"Error checking join: {e}")
        return True

# Join buttons template
def get_join_markup():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME}"),
            InlineKeyboardButton("💬 Join Group", url=f"https://t.me/{GROUP_USERNAME}")
        ],
        [InlineKeyboardButton("🔄 Try Again", callback_data="check_again")]
    ])

# Main menu buttons
def get_main_markup():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👥 Support Group", url=f"https://t.me/{GROUP_USERNAME}"),
            InlineKeyboardButton("📢 Channel", url=f"https://t.me/{CHANNEL_USERNAME}")
        ],
        [
            InlineKeyboardButton("🚀 Share Bot", url=f"https://t.me/share/url?url=https://t.me/{BOT_USERNAME}?start=true&text=Hey! Checkout this awesome Media Downloader Bot 🔥")
        ]
    ])

@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    user_id = message.from_user.id
    if not await is_user_joined(client, user_id):
        await message.reply_text(
            "⚠️ **Aapne Hamara Channel Ya Group Join Nahi Kiya Hai!**\n\n"
            "Bot ka use karne ke liye niche diye gaye dono channels ko join karein.",
            reply_markup=get_join_markup()
        )
        return
        
    await message.reply_text(
        f"👋 **Hello {message.from_user.first_name}! Welcome to Media Downloader Bot.**\n\n"
        "Mujhe kisi bhi **Instagram Reels, YouTube Shorts, ya Facebook Video** ka link bhejo, "
        "mai use direct download karke bhej dunga!\n\n"
        "💡 Use `/help` to know more.",
        reply_markup=get_main_markup()
    )

@app.on_message(filters.command("help") & filters.private)
async def help_cmd(client, message):
    await message.reply_text(
        "📖 **Bot Kaise Use Karein?**\n\n"
        "1. Kisi bhi App (Instagram/YouTube/Facebook) par jayein.\n"
        "2. Video ka **Copy Link** karne ke baad yahan chat me paste kar dein.\n"
        "3. Bot use automatic download karke aapko bhej dega.",
        reply_markup=get_main_markup()
    )

@app.on_callback_query(filters.regex("check_again"))
async def check_again_callback(client, callback_query):
    user_id = callback_query.from_user.id
    if await is_user_joined(client, user_id):
        await callback_query.message.edit_text(
            f"🎉 **Dhananyawad Join Karne Ke Liye!**\n\n"
            "Ab aap mujhe koi bhi link bhej sakte hain, mai use download kar dunga! 🔥",
            reply_markup=get_main_markup()
        )
        await callback_query.answer("✅ Access Granted!")
    else:
        await callback_query.answer("❌ Pehle dono channels join karein!", show_alert=True)

@app.on_message(filters.regex(r"https?://(www\.)?(instagram\.com|youtube\.com|youtu\.be|facebook\.com|fb\.watch)/.+") & filters.private)
async def download_video(client, message):
    user_id = message.from_user.id
    if not await is_user_joined(client, user_id):
        await message.reply_text("⚠️ **Pehle Join Karein!**", reply_markup=get_join_markup())
        return

    url = message.text
    chat_id = message.chat.id
    m = await message.reply_text("🔎 **Processing your link... Please wait...**")
    video_filename = f"video_{message.id}.mp4"

    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': video_filename,
        'quiet': True,
        'no_warnings': True
    }

    try:
        await m.edit("📥 **Downloading video from server...**")
        loop = asyncio.get_event_loop()
        with YoutubeDL(ydl_opts) as ydl:
            await loop.run_in_executor(None, lambda: ydl.download([url]))

        if os.path.exists(video_filename):
            await m.edit("🚀 **Uploading to Telegram...**")
            await client.send_video(
                chat_id=chat_id,
                video=video_filename,
                caption=f"✨ **Downloaded Successfully by @{BOT_USERNAME}**",
                reply_markup=get_main_markup()
            )
            os.remove(video_filename)
            await m.delete()
        else:
            await m.edit("❌ **Error:** Video file nahi mil saki.")
    except Exception as e:
        await m.edit(f"❌ **An error occurred:**\n`{str(e)}`")
        if os.path.exists(video_filename):
            os.remove(video_filename)

# --- BULLETPROOF ASYNC ENGINE FOR PYTHON 3.11+ ---
async def start_bot():
    print("🤖 Downloader Bot is starting...")
    await app.start()
    print("🚀 Bot is fully upgraded and running live!")
    await idle()
    await app.stop()

if __name__ == "__main__":
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        pass

import os
import asyncio
from pyrogram import Client, filters, idle
from pyrogram.errors import UserNotParticipant, ChatAdminRequired, PeerIdInvalid
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from yt_dlp import YoutubeDL

# ---- CONFIGURATION ----
API_ID = 20060680          # Aapki sahi API ID (Bina quotes ke integer)
API_HASH = "fb7e080bc19d911c14f758b39605febc" # Apna API HASH
BOT_TOKEN = "8709264133:AAFbUfYU1dgOuLaynhitaRHZRP1Tt9UxiEE" # Apna Bot Token

BOT_USERNAME = "SheinFrsh_bot"        
CHANNEL_USERNAME = "offerfactorynew"    
GROUP_USERNAME = "AllcontentNew"        
# -----------------------

app = Client("MediaDownloaderBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Force join check karne ka safe function
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

# Safe links templates
def get_join_markup():
    # .lower() lagane se username ekdum clean small letters me sahi link banayega
    c_link = f"https://t.me/{CHANNEL_USERNAME.strip()}"
    g_link = f"https://t.me/{GROUP_USERNAME.strip()}"
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📢 Join Channel", url=c_link),
            InlineKeyboardButton("💬 Join Group", url=g_link)
        ],
        [InlineKeyboardButton("🔄 Try Again", callback_data="check_again")]
    ])

def get_main_markup():
    c_link = f"https://t.me/{CHANNEL_USERNAME.strip()}"
    g_link = f"https://t.me/{GROUP_USERNAME.strip()}"
    b_link = f"https://t.me/{BOT_USERNAME.strip()}?start=true"
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📢 Channel", url=c_link),
            InlineKeyboardButton("💬 Support", url=g_link)
        ],
        [
            InlineKeyboardButton("🚀 Share Bot", url=f"https://t.me/share/url?url={b_link}&text=Best Downloader Bot!")
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
        f"👋 **Hello {message.from_user.first_name}! Welcome.**\n\n"
        "Mujhe kisi bhi **Instagram Reels, YouTube Shorts, ya Facebook Video** ka link bhejo, "
        "mai use direct download karke bhej dunga!\n\n"
        "💡 Use `/help` to know more.",
        reply_markup=get_main_markup()
    )

@app.on_message(filters.command("help") & filters.private)
async def help_cmd(client, message):
    await message.reply_text(
        "📖 **Bot Kaise Use Karein?**\n\n"
        "1. Kisi bhi video ka link copy karein.\n"
        "2. Use yahan chat me seedhe send kar dein.\n"
        "3. Bot use automatic download karke aapko bhej dega.",
        reply_markup=get_main_markup()
    )

@app.on_callback_query(filters.regex("check_again"))
async def check_again_callback(client, callback_query):
    user_id = callback_query.from_user.id
    if await is_user_joined(client, user_id):
        await callback_query.message.edit_text(
            "🎉 **Dhananyawad Join Karne Ke Liye!**\n\n"
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

# --- Standard Continuous Engine ---
if __name__ == "__main__":
    print("🚀 Starting Bot Engine...")
    app.run()

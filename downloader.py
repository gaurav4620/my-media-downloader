import os
import asyncio
from pyrogram import Client, filters
from pyrogram.errors import UserNotParticipant, ChatAdminRequired, PeerIdInvalid
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from yt_dlp import YoutubeDL

# ---- CONFIGURATION ----
API_ID = 20060680          # Apni API ID dalein (Integer me)
API_HASH = "fb7e080bc19d911c14f758b39605febc" # Apna API HASH dalein
BOT_TOKEN = "8709264133:AAFbUFYU1dgOuLaynhitaRHZRP1Tt9UxiEE" # Apna Bot Token dalein

# Usernames me '@' bilkul MAT lagana, sirf name likhna
BOT_USERNAME = "SheinFrsh_bot"        # Aapke bot ka sahi username
CHANNEL_USERNAME = "offerfactorynew"    # Aapke channel ka username
GROUP_USERNAME = "AllcontentNew"        # Aapke group ka username
# -----------------------

app = Client("MediaDownloaderBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Force Join Check karne ka naya aur secure function
async def check_force_join(client, message):
    chat_id = message.chat.id
    
    # Agar config abhi tak change nahi ki hai to bypass na ho
    if CHANNEL_USERNAME == "your_channel" or GROUP_USERNAME == "your_group":
        return True

    try:
        # Check Channel
        await client.get_chat_member(CHANNEL_USERNAME, chat_id)
        # Check Group
        await client.get_chat_member(GROUP_USERNAME, chat_id)
        return True
        
    except UserNotParticipant:
        # Agar user member nahi hai
        await message.reply_text(
            "⚠️ **Aapne Hamara Channel Ya Group Join Nahi Kiya Hai!**\n\n"
            "Bot ka use karne ke liye niche diye gaye dono buttons par click karke join karein, aur fir **Try Again** par click karein.",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME}"),
                    InlineKeyboardButton("💬 Join Group", url=f"https://t.me/{GROUP_USERNAME}")
                ],
                [
                    InlineKeyboardButton("🔄 Try Again", url=f"https://t.me/{BOT_USERNAME}?start=true")
                ]
            ])
        )
        return False
        
    except (ChatAdminRequired, PeerIdInvalid):
        # Agar bot channel/group me admin nahi hai to ye message dikhega
        await message.reply_text(
            "❌ **Developer Setup Error:**\n"
            f"Kripya dhyan dein ki bot ko `@ {CHANNEL_USERNAME}` aur `@ {GROUP_USERNAME}` dono me **Admin** banana zaroori hai! Varna force join kaam nahi karega."
        )
        return False
    except Exception as e:
        print(f"Error in force join: {e}")
        return True

@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    if not await check_force_join(client, message):
        return
        
    await message.reply_text(
        f"👋 **Welcome to Media Downloader Bot!**\n\n"
        "Mujhe kisi bhi **Instagram Reels, YouTube Shorts, ya Facebook Video** ka link bhejo, "
        "mai use direct download karke bhej dunga!"
    )

@app.on_message(filters.regex(r"https?://(www\.)?(instagram\.com|youtube\.com|youtu\.be|facebook\.com|fb\.watch)/.+") & filters.private)
async def download_video(client, message):
    if not await check_force_join(client, message):
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
                caption=f"✨ **Downloaded Successfully by @{BOT_USERNAME}**\n\n📢 Join: @{CHANNEL_USERNAME}"
            )
            
            os.remove(video_filename)
            await m.delete()
        else:
            await m.edit("❌ **Error:** Video file nahi mil saki.")

    except Exception as e:
        await m.edit(f"❌ **An error occurred:**\n`{str(e)}`")
        if os.path.exists(video_filename):
            os.remove(video_filename)

if __name__ == "__main__":
    print("🤖 Downloader Bot is fully upgraded and running...")
    
    # Naye Python versions ke liye event loop handle karna
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    loop.run_until_complete(app.run())

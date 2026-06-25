import os
import asyncio
import sqlite3
from pyrogram import Client, filters, idle
from pyrogram.errors import UserNotParticipant, FloodWait
from yt_dlp import YoutubeDL

# ---- CONFIGURATION (Railway Variables Se Uthayega) ----
API_ID = int(os.getenv("API_ID", "20060680"))
API_HASH = os.getenv("API_HASH", "fb7e080bc19d911c14f758b39605febc")
BOT_TOKEN = os.getenv("BOT_TOKEN")

BOT_USERNAME = os.getenv("BOT_USERNAME", "SheinFrsh_bot")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "offerfactorynew")
GROUP_USERNAME = os.getenv("GROUP_USERNAME", "AllcontentNew")
ADMIN_ID = int(os.getenv("ADMIN_ID", "554649415"))
# -------------------------------------------------------

app = Client("MediaDownloaderBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ---- DATABASE SETUP (SQLite) ----
DB_NAME = "users.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)''')
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass 
    finally:
        conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users

def get_users_count():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count

# --- AUTOMATIC PROFILE/BIO UPDATER TASK ---
async def auto_update_profile():
    while True:
        try:
            count = get_users_count()
            new_bio = f"🔥 Total Active Users: {count} | Send me any link to download video instantly! 🚀"
            await app.set_bot_info(description=new_bio)
            print(f"✨ Bot Profile Description updated with {count} users!")
        except Exception as e:
            print(f"Error updating profile description: {e}")
        await asyncio.sleep(600)

# Force join check karne ka function
async def is_user_joined(client, user_id):
    try:
        await client.get_chat_member(CHANNEL_USERNAME, user_id)
        await client.get_chat_member(GROUP_USERNAME, user_id)
        return True
    except UserNotParticipant:
        return False
    except Exception as e:
        print(f"Error checking join: {e}")
        return True

@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    user_id = message.from_user.id
    add_user(user_id)
    
    if not await is_user_joined(client, user_id):
        await message.reply_text(
            "⚠️ **Aapne Hamara Channel Ya Group Join Nahi Kiya!**\n\n"
            f"Bot use karne ke liye pehle hamara Channel (@{CHANNEL_USERNAME}) aur Group (@{GROUP_USERNAME}) join karein, fir dobara `/start` likhein."
        )
        return
        
    await message.reply_text(
        f"👋 **Hello {message.from_user.first_name}!**\n\n"
        "Mujhe kisi bhi **Instagram Reels, YouTube Shorts, ya Facebook Video** ka link bhejo, mai use direct download karke bhej dunga!"
    )

# ---- ADMIN COMMANDS ----
@app.on_message(filters.command("stats") & filters.user(ADMIN_ID) & filters.private)
async def stats_cmd(client, message):
    count = get_users_count()
    await message.reply_text(f"📊 **Bot Statistics:**\n\n👤 **Total Users:** {count}")

@app.on_message(filters.command("broadcast") & filters.user(ADMIN_ID) & filters.private)
async def broadcast_cmd(client, message):
    if not message.reply_to_message:
        return await message.reply_text("❌ **Galti:** Kisi message ka reply karke `/broadcast` likho!")
    
    exmsg = await message.reply_text("📢 **Broadcast shuru ho raha hai... Please wait...**")
    all_users = get_all_users()
    
    success = 0
    failed = 0
    
    for u_id in all_users:
        try:
            await message.reply_to_message.copy(chat_id=u_id)
            success += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await message.reply_to_message.copy(chat_id=u_id)
            success += 1
        except Exception:
            failed += 1
            
    await exmsg.edit(
        f"📢 **Broadcast Completed!**\n\n"
        f"✅ **Success:** {success} users\n"
        f"❌ **Failed:** {failed} users"
    )

@app.on_message(filters.regex(r"https?://(www\.)?(instagram\.com|youtube\.com|youtu\.be|facebook\.com|fb\.watch)/.+") & filters.private)
async def download_video(client, message):
    user_id = message.from_user.id
    add_user(user_id)
    
    if not await is_user_joined(client, user_id):
        await message.reply_text(
            f"⚠️ **Pehle Join Karein!**\n\nChannel: @{CHANNEL_USERNAME}\nGroup: @{GROUP_USERNAME}"
        )
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
                caption=f"✨ **Downloaded Successfully by @{BOT_USERNAME}**"
            )
            os.remove(video_filename)
            await m.delete()
        else:
            await m.edit("❌ **Error:** Video file nahi mil saki.")
    except Exception as e:
        await m.edit(f"❌ **An error occurred:**\n`{str(e)}`")
        if os.path.exists(video_filename):
            os.remove(video_filename)

# --- Background Task Connection Engine ---
async def main():
    print("🚀 Initializing Database...")
    init_db()
    print("🤖 Starting Bot Engine...")
    await app.start()
    asyncio.create_task(auto_update_profile())
    print("🚀 Bot is live and Auto-Bio Updater is active!")
    await idle()
    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())

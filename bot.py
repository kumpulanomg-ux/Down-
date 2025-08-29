import os
import re
import asyncio
import aiohttp
import tempfile
import time
import traceback
import yt_dlp
import json
import shutil
from urllib.parse import urlparse, quote
from youtubesearchpython import SearchVideos
from collections import defaultdict
from typing import Dict, Optional
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery
)


'''• أول فريق مصري متخصص في تطوير بايثون Python   
• القناة #Code الرسميـة الرائدة في تـعليم البرمجة عربيًا 
• جميع الحقوق و النشر محفوظة:  ©️ VEGA™ 2015  
• مطور ومُنشئ المحتوى:  
• @TopVeGa
• @DevVeGa
'''

API_ID = int(os.getenv('API_ID', 24514748))
API_HASH = os.getenv('API_HASH', '5dbe5df68358919d32cbfd341e0142f1')
BOT_TOKEN = os.getenv('BOT_TOKEN', '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')

app = Client("social_downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)



downloads_path = "downloads"
os.makedirs(downloads_path, exist_ok=True)



'''• أول فريق مصري متخصص في تطوير بايثون Python   
• القناة #Code الرسميـة الرائدة في تـعليم البرمجة عربيًا 
• جميع الحقوق و النشر محفوظة:  ©️ VEGA™ 2015  
• مطور ومُنشئ المحتوى:  
• @TopVeGa
• @DevVeGa
'''


YOUTUBE_OPTS = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
    'outtmpl': f'{downloads_path}/%(title)s.%(ext)s',
    'writethumbnail': True,
    'quiet': True,
    'cookiefile': 'cookies.txt',
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.youtube.com/',
        'DNT': '1'
    }
}



TIKTOK_OPTS = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
    'outtmpl': f'{downloads_path}/%(title)s.%(ext)s',
    'writethumbnail': True,
    'quiet': True,
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.tiktok.com/',
        'DNT': '1'
    }
}


SNAPCHAT_OPTS = {
    'format': 'best[ext=mp4]/best',
    'quiet': True,
    'no_warnings': True,
    'force_generic_extractor': True,
    'socket_timeout': 30,
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1'
    },
    'extractor_args': {
        'snapchat': {
            'skip_auth': True
        }
    }
}


SOUNDCLOUD_OPTS = {
    'format': 'bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'force_generic_extractor': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://soundcloud.com/',
        'DNT': '1'
    }
}


FACEBOOK_OPTS = {
    'format': 'best[ext=mp4]',
    'quiet': True,
    'no_warnings': True,
    'force_generic_extractor': True,
    'cookiefile': 'cookies.txt',
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Referer': 'https://www.facebook.com/',
    },
}



'''• أول فريق مصري متخصص في تطوير بايثون Python   
• القناة #Code الرسميـة الرائدة في تـعليم البرمجة عربيًا 
• جميع الحقوق و النشر محفوظة:  ©️ VEGA™ 2015  
• مطور ومُنشئ المحتوى:  
• @TopVeGa
• @DevVeGa
'''


user_states = defaultdict(dict)
last_progress = defaultdict(int) 


def clean_filename(name):
    return re.sub(r'[\\/:"*?<>|]', '', name)


def fix_facebook_url(url):
    patterns = [
        r'(?:https?://)?(?:www\.|m\.)?facebook\.com/(?:[^/]+/videos/|watch/\?v=|share/v/|reel/)([0-9]+)',
        r'(?:https?://)?(?:www\.|m\.)?fb\.watch/([a-zA-Z0-9_-]+)',
        r'(?:https?://)?(?:www\.|m\.)?facebook\.com/(?:video\.php\?v=|story\.php\?story_fbid=)([0-9]+)'
    ]    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            return f"https://www.facebook.com/watch/?v={video_id}"    
    return url


async def get_facebook_video_info(url: str):
    try:
        try:
            return await asyncio.to_thread(get_fb_video_info_sync, url)
        except Exception as e:
            print(f"المحاولة الأولى فشلت: {e}")
            os.system("pip install -U yt-dlp")
            return await asyncio.to_thread(get_fb_video_info_sync, url)
    except Exception as e:
        raise Exception(f"فشل في تحميل معلومات الفيديو: {str(e)}")

def get_fb_video_info_sync(url: str):
    try:
        with yt_dlp.YoutubeDL(FACEBOOK_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)
            best_url = None
            if 'formats' in info:
                for f in info['formats']:
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                        if not best_url or f.get('height', 0) > best_url.get('height', 0):
                            best_url = f
            video_url = best_url['url'] if best_url else info['url']            
            return {
                'title': info.get('title', 'فيديو فيسبوك'),
                'url': video_url,
                'thumbnail': info.get('thumbnail', ''),
                'duration': info.get('duration', 0)
            }
    except Exception as e:
        raise Exception(f"خطأ في استخراج المعلومات: {str(e)}")


async def download_video(url: str, service: str, is_audio=False):
    try:
        if service == "facebook":
            return await get_facebook_video_info(url)
        if service == "tiktok":
            opts = TIKTOK_OPTS
        elif service == "snapchat":
            opts = SNAPCHAT_OPTS
        elif service == "soundcloud":
            opts = SOUNDCLOUD_OPTS
        else:  #
            opts = YOUTUBE_OPTS
        if is_audio:
            opts = {
                **opts,
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
            }
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, "video")
        opts['outtmpl'] = temp_file + '.%(ext)s'
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            if is_audio:
                file_path = os.path.splitext(file_path)[0] + '.mp3'
            thumbnail = info.get('thumbnail', '')
            thumb_file = None
            if thumbnail:
                async with aiohttp.ClientSession() as session:
                    async with session.get(thumbnail) as response:
                        if response.status == 200:
                            thumb_path = os.path.join(temp_dir, "thumb.jpg")
                            with open(thumb_path, 'wb') as f:
                                f.write(await response.read())
                            thumb_file = thumb_path            
            return {
                'title': info.get('title', f'محتوى {service}'),
                'path': file_path,
                'thumbnail': thumb_file,
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Unknown'),
                'temp_dir': temp_dir,
                'url': url
            }            
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        if "This video is only available for registered users" in error_msg:
            raise Exception("هذا المحتوى متاح فقط للمستخدمين المسجلين")
        elif "Private video" in error_msg:
            raise Exception("هذا الفيديو خاص ولا يمكن الوصول إليه")
        elif "Content unavailable" in error_msg:
            raise Exception("المحتوى غير متوفر أو تم حذفه")
        else:
            raise Exception(f"خطأ في التحميل: {error_msg}")
    
    except Exception as e:
        raise Exception(f"خطأ غير متوقع: {str(e)}")



async def download_thumbnail(url):
    if not url:
        return None        
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    thumb_data = await response.read()
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as f:
                        f.write(thumb_data)
                        return f.name
    except Exception as e:
        print(f"فشل تحميل الصورة المصغرة: {e}")
        return None

async def download_video_with_progress(url, file_path, msg, is_audio=False):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return False               
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                last_update = 0
                start_time = time.time()
                
                with open(file_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(1024*1024):
                        if not chunk:
                            break                            
                        f.write(chunk)
                        downloaded += len(chunk)
                        now = time.time()
                        if now - last_update > 3 or downloaded == total_size:
                            percent = (downloaded / total_size) * 100
                            elapsed = now - start_time
                            speed = downloaded / elapsed if elapsed > 0 else 0
                            remaining = (total_size - downloaded) / speed if speed > 0 else 0                            
                            file_type = "الصوتي" if is_audio else "الفيديو"
                            status = (
                                f"⬇️ جاري تحميل {file_type}...\n"
                                f"📊 {percent:.1f}% - {downloaded//(1024*1024)}MB / {total_size//(1024*1024)}MB\n"
                                f"🚀 السرعة: {speed/(1024*1024):.1f} MB/s\n"
                                f"⏱ المتبقي: {remaining:.0f} ثانية"
                            )                            
                            await msg.edit_text(status)
                            last_update = now                
                return True
    except Exception as e:
        print(f"خطأ في تحميل الفيديو: {e}")
        return False

async def progress_callback(current, total, msg):
    try:
        percent = int((current / total) * 100)
        if percent > last_progress.get(msg.id, 0) or percent == 100:
            await msg.edit_text(f"📤 جاري الرفع... {percent}%")
            last_progress[msg.id] = percent            
    except Exception as e:
        print(f"خطأ في تتبع التقدم: {e}")


async def process_and_send(client, message, url, service, is_audio=False):
    try:
        processing_msg = await message.reply_text(f"⏳ جاري معالجة الرابط...")
        content_info = await download_video(url, service, is_audio)
        if service == "facebook":
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
                video_file_path = temp_video.name
            await processing_msg.edit_text("⬇️ جاري تحميل الفيديو...")
            download_success = await download_video_with_progress(
                content_info['url'],
                video_file_path,
                processing_msg
            )            
            if not download_success:
                await processing_msg.edit_text("❌ فشل في تحميل الفيديو")
                os.unlink(video_file_path)
                return
            content_info['path'] = video_file_path
            content_info['temp_file'] = True
        else:
            pass
        thumb_file = None
        if content_info.get('thumbnail'):
            thumb_file = await download_thumbnail(content_info['thumbnail'])
        await processing_msg.edit_text("📤 جاري الرفع...")        
        if service == "soundcloud" or is_audio:
            await message.reply_audio(
                content_info['path'],
                caption=f"🎵 **{content_info['title']}**\n\nتم التحميل بواسطة @{client.me.username}",
                title=clean_filename(content_info['title']),
                performer=content_info.get('uploader', 'Unknown'),
                thumb=thumb_file,
                duration=int(content_info.get('duration', 0)),
                progress=progress_callback,
                progress_args=(processing_msg,)
            )
        else:
            await message.reply_video(
                content_info['path'],
                caption=f"🎬 **{content_info['title']}**\n\nتم التحميل بواسطة @{client.me.username}",
                thumb=thumb_file,
                duration=int(content_info.get('duration', 0)),
                supports_streaming=True,
                progress=progress_callback,
                progress_args=(processing_msg,)
            )
        await processing_msg.delete()
        if 'temp_dir' in content_info and os.path.exists(content_info['temp_dir']):
            shutil.rmtree(content_info['temp_dir'])
        if content_info.get('path') and os.path.exists(content_info['path']):
            if content_info.get('temp_file'):
                os.unlink(content_info['path'])
            else:
                os.unlink(content_info['path'])
        if thumb_file and os.path.exists(thumb_file):
            os.unlink(thumb_file)            
    except Exception as e:
        error_msg = f"❌ حدث خطأ أثناء معالجة المحتوى:\n{str(e)}"
        await message.reply_text(error_msg)
        traceback.print_exc()
        if 'processing_msg' in locals():
            await processing_msg.delete()
        if 'content_info' in locals():
            if content_info.get('path') and os.path.exists(content_info['path']):
                os.unlink(content_info['path'])
            if 'temp_dir' in content_info and os.path.exists(content_info['temp_dir']):
                shutil.rmtree(content_info['temp_dir'])
            if thumb_file and os.path.exists(thumb_file):
                os.unlink(thumb_file)




'''• أول فريق مصري متخصص في تطوير بايثون Python   
• القناة #Code الرسميـة الرائدة في تـعليم البرمجة عربيًا 
• جميع الحقوق و النشر محفوظة:  ©️ VEGA™ 2015  
• مطور ومُنشئ المحتوى:  
• @TopVeGa
• @DevVeGa
'''


@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("تحميل من فيس بوك", callback_data="facebook"),
        InlineKeyboardButton("تحميل من تيك توك", callback_data="tiktok")],
        [InlineKeyboardButton("تحميل من اليوتيوب", callback_data="youtube")],
        [InlineKeyboardButton("تحميل من اسناب شات", callback_data="snapchat"),
        InlineKeyboardButton("تحميل من SoundCloud", callback_data="soundcloud")],
        [InlineKeyboardButton("مساعدة", callback_data="help")]
    ])    
    await message.reply_text(
        "مرحباً! 👋 أنا بوت تحميل الفيديوهات من:\n"
        "- الفيسبوك\n- تيك توك\n- اليوتيوب\n- اسناب شات\n- SoundCloud\n\n"
        "اختر الخدمة التي تريدها من الأزرار أدناه:",
        reply_markup=keyboard
    )

@app.on_callback_query()
async def handle_callback(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    data = callback_query.data    
    if data == "facebook":
        user_states[user_id] = {"state": "waiting_facebook"}
        await callback_query.message.edit_text(
            "أرسل رابط فيديو الفيسبوك الآن",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("العودة", callback_data="back")]
            ])
        )        
    elif data == "tiktok":
        user_states[user_id] = {"state": "waiting_tiktok"}
        await callback_query.message.edit_text(
            "أرسل رابط فيديو تيك توك الآن",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("العودة", callback_data="back")]
            ])
        )
    elif data == "snapchat":
        user_states[user_id] = {"state": "waiting_snapchat"}
        await callback_query.message.edit_text(
            "أرسل رابط فيديو اسناب شات الآن",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("العودة", callback_data="back")]
            ])
        )        
    elif data == "soundcloud":
        user_states[user_id] = {"state": "waiting_soundcloud"}
        await callback_query.message.edit_text(
            "أرسل رابط مقطع SoundCloud الآن",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("العودة", callback_data="back")]
            ])
        )
    elif data == "youtube":
        user_states[user_id] = {"state": "waiting_youtube_type"}
        await callback_query.message.edit_text(
            "◍ اختر نوع التحميل من اليوتيوب:",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("تحميل صوت", callback_data="youtube_audio"),
                    InlineKeyboardButton("تحميل فيديو", callback_data="youtube_video")
                ],
                [InlineKeyboardButton("العودة", callback_data="back")]
            ])
        )
    elif data == "youtube_audio":
        user_states[user_id] = {"state": "waiting_youtube", "type": "audio_dl"}
        await callback_query.message.edit_text(
            "أرسل رابط أو اسم فيديو اليوتيوب الآن",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("العودة", callback_data="back")]
            ])
        )
    elif data == "youtube_video":
        user_states[user_id] = {"state": "waiting_youtube", "type": "video_dl"}
        await callback_query.message.edit_text(
            "أرسل رابط أو اسم فيديو اليوتيوب الآن",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("العودة", callback_data="back")]
            ])
        )
    elif data == "help":
        help_text = (
            "❓ **مساعدة استخدام البوت**\n\n"
            "1. اختر الخدمة التي تريدها (فيسبوك، تيك توك، يوتيوب، اسناب شات، SoundCloud)\n"
            "2. أرسل رابط الفيديو أو المقطع الصوتي\n"
            "3. انتظر حتى يتم تحميل المحتوى وإرساله إليك\n\n"
            "ملاحظات:\n"
            "- قد تستغرق عملية التحميل بعض الوقت حسب حجم المحتوى\n"
            "- البوت يدعم معظم الروابط من المنصات المدعومة\n"
            "- في حالة وجود مشاكل، حاول مرة أخرى أو أرسل رابط مختلف\n"
            "- SoundCloud: يدعم تحميل المقاطع الصوتية فقط"
        )
        await callback_query.message.edit_text(
            help_text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("العودة", callback_data="back")]
            ])
        )        
    elif data == "back":
        user_states.pop(user_id, None)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("تحميل من فيس بوك", callback_data="facebook"),
            InlineKeyboardButton("تحميل من تيك توك", callback_data="tiktok")],
            [InlineKeyboardButton("تحميل من اليوتيوب", callback_data="youtube")],
            [InlineKeyboardButton("تحميل من اسناب شات", callback_data="snapchat"),
            InlineKeyboardButton("تحميل من SoundCloud", callback_data="soundcloud")],
            [InlineKeyboardButton("مساعدة", callback_data="help")]
        ])
        await callback_query.message.edit_text(
            "اختر الخدمة التي تريدها من الأزرار أدناه:",
            reply_markup=keyboard
        )


@app.on_message(filters.text & ~filters.regex("^/"))
async def handle_links(client: Client, message: Message):
    user_id = message.from_user.id
    user_state = user_states.get(user_id, {})
    text = message.text.strip()
    urls = re.findall(r'https?://[^\s]+', text)
    if not urls:
        if user_state.get("state") == "waiting_youtube" and text:
            download_type = user_state.get("type", "video_dl")
            try:
                video_data = await search_youtube(text)
                if not video_data:
                    await message.reply_text("❌ لم يتم العثور على نتائج")
                    return                
                url = video_data["link"]
                await process_and_send(client, message, url, "youtube", download_type == "audio_dl")
                user_states.pop(user_id, None)
            except Exception as e:
                await message.reply_text(f"❌ حدث خطأ: {str(e)}")
            return
        else:
            await message.reply_text("⚠️ لم أجد أي رابط في رسالتك. أرسل رابط فيديو صحيح.")
            return    
    url = urls[0].strip()
    service = None
    is_audio = False
    if user_state.get("state") == "waiting_facebook" or re.match(r'https?://(?:www\.|m\.)?(?:facebook\.com|fb\.watch|fb\.com|fb\.me)/[^\s]+', url):
        service = "facebook"
        user_states.pop(user_id, None)        
    elif user_state.get("state") == "waiting_tiktok" or re.match(r'https?://(?:www\.|vm\.|vt\.)?tiktok\.com/[^\s]+', url):
        service = "tiktok"
        user_states.pop(user_id, None)        
    elif user_state.get("state") == "waiting_snapchat" or re.match(r'https?://(?:www\.)?snapchat\.com/[^\s]+', url):
        service = "snapchat"
        user_states.pop(user_id, None)        
    elif user_state.get("state") == "waiting_soundcloud" or re.match(r'https?://(?:www\.)?soundcloud\.com/[^\s]+', url) or re.match(r'https?://(?:on\.)?soundcloud\.com/[^\s]+', url):
        service = "soundcloud"
        user_states.pop(user_id, None)
        is_audio = True        
    elif user_state.get("state") == "waiting_youtube" or re.match(r'https?://(?:www\.)?(?:youtube\.com|youtu\.be)/[^\s]+', url):
        service = "youtube"
        user_states.pop(user_id, None)
        is_audio = user_state.get("type", "video_dl") == "audio_dl"
    if service:
        try:
            if service == "facebook":
                fixed_url = fix_facebook_url(url)
                if fixed_url != url:
                    await message.reply_text(f"🔧 تم إصلاح الرابط إلى: {fixed_url}")
                    url = fixed_url            
            await process_and_send(client, message, url, service, is_audio)                
        except Exception as e:
            await message.reply_text(f"❌ حدث خطأ: {str(e)}")
            traceback.print_exc()
    else:
        await message.reply_text(
            "⚠️ لم أتعرف على نوع الرابط. يرجى اختيار الخدمة أولاً.\n"
            "استخدم /start لفتح القائمة الرئيسية.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("فتح القائمة", callback_data="back")]
            ])
        )

async def search_youtube(query: str) -> Optional[Dict]:
    try:
        search = SearchVideos(query, offset=1, mode="dict", max_results=1)
        result = search.result().get("search_result", [])
        return result[0] if result else None
    except Exception:
        return None



'''• أول فريق مصري متخصص في تطوير بايثون Python   
• القناة #Code الرسميـة الرائدة في تـعليم البرمجة عربيًا 
• جميع الحقوق و النشر محفوظة:  ©️ VEGA™ 2015  
• مطور ومُنشئ المحتوى:  
• @TopVeGa
• @DevVeGa
'''



if __name__ == "__main__":
    os.system("pip install -U yt-dlp")
    print("✅ تم تشغيل البوت بنجاح...")
    app.run()

import yt_dlp
import os
import subprocess

# Step 0: Create folders for organization
os.makedirs("data/raw_audio", exist_ok=True)
print("✅ Created folder: data/raw_audio")

# Step 1: Get YouTube URL
youtube_url = input("Enter YouTube URL: ").strip()

# Step 2: Define output MP3 path
output_mp3 = os.path.join("data", "raw_audio", "full_audio.mp3")

# Step 3: Set yt_dlp options to force mp3 conversion
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'data/raw_audio/temp_audio.%(ext)s',  # Download to raw_audio folder
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'quiet': False,
}

print("📥 Downloading and converting...")
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([youtube_url])

# Step 4: Rename to final name if conversion succeeded
temp_mp3 = os.path.join("data", "raw_audio", "temp_audio.mp3")
if os.path.exists(temp_mp3):
    os.rename(temp_mp3, output_mp3)
    print(f"✅ Saved audio as: {output_mp3}")
else:
    print("❌ MP3 not found. Check if ffmpeg is installed and accessible.")

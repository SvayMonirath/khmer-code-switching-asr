import os
import subprocess
import glob

# Create chunks folder
os.makedirs("data/chunks", exist_ok=True)

# Path to full audio
input_audio = "data/raw_audio/full_audio.mp3"

# Ask user for chunk length in seconds
while True:
    try:
        chunk_length = int(input("\n\nEnter chunk length in seconds (e.g., 10): ").strip())
        if chunk_length <= 0:
            print("Please enter a positive integer.")
            continue
        break
    except ValueError:
        print("Invalid input. Please enter an integer.")

# Output pattern for chunk files
output_pattern = "data/chunks/chunk_%03d.wav"

# Run ffmpeg to chunk audio with output suppressed
print(f"Chunking full audio into {chunk_length}-second WAV files...")
subprocess.run([
    "ffmpeg",
    "-hide_banner",
    "-loglevel", "error",
    "-i", input_audio,
    "-ar", "16000",
    "-ac", "1",
    "-f", "segment",
    "-segment_time", str(chunk_length),
    "-reset_timestamps", "1",
    output_pattern
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# List created chunks
chunk_files = sorted(glob.glob("data/chunks/chunk_*.wav"))
print(f"✅ Created {len(chunk_files)} chunks.")

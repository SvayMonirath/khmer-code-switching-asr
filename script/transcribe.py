import os
import glob
import re
import time
import torch
from transformers import pipeline

# ========== [CONFIG] ==========
CHUNK_FOLDER = "data/chunks"
TRANSCRIPT_FOLDER = "data/transcriptions"
MODEL_NAME = "Vira21/Whisper-Small-Khmer"
# ==============================

# Extract chunk number for sorting
def extract_number(filename):
    match = re.search(r'chunk_(\d+)\.wav', os.path.basename(filename))
    return int(match.group(1)) if match else -1

# Select device
device = 0 if torch.cuda.is_available() else -1
print(f"[INFO] Using device: {'GPU' if device == 0 else 'CPU'}")

# Load Whisper model
print("[INFO] Loading ASR model...")
asr = pipeline("automatic-speech-recognition", model=MODEL_NAME, device=device)
print("[INFO] Model loaded successfully.\n")

# Prepare folders
os.makedirs(TRANSCRIPT_FOLDER, exist_ok=True)

# Load and sort chunk files
audio_files = glob.glob(os.path.join(CHUNK_FOLDER, "chunk_*.wav"))
audio_files.sort(key=extract_number)

if not audio_files:
    print(f"[ERROR] No audio chunk files found in {CHUNK_FOLDER}.")
    exit(1)

print(f"[INFO] Found {len(audio_files)} chunk files.\n")

# ========== [TRANSCRIPTION LOOP] ==========
for audio_file in audio_files:
    base_name = os.path.splitext(os.path.basename(audio_file))[0]
    output_file = os.path.join(TRANSCRIPT_FOLDER, base_name + ".txt")

    if os.path.exists(output_file):
        print(f"[SKIP] Transcription exists for {audio_file}.")
        continue

    print(f"[TRANSCRIBING] {audio_file} ...")
    start_time = time.time()

    try:
        result = asr(audio_file)
        transcription = result['text']
    except Exception as e:
        print(f"[ERROR] Failed to transcribe {audio_file}: {e}")
        continue

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(transcription)

    duration = time.time() - start_time
    print(f"[SAVED] {output_file} ({duration:.2f} sec)\n")

print("[✅ DONE] All audio files transcribed.")

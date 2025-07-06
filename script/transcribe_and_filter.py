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
CLEANUP_BATCH = 100  # number of files to batch-clean
# ==============================

# Check for Khmer + English (code-switching)
def contains_khmer_and_english(text):
    has_khmer = re.search(r'[\u1780-\u17FF]', text)
    has_english = re.search(r'[A-Za-z]', text)
    return has_khmer and has_english

# Extract chunk number for sorting
def extract_number(filename):
    match = re.search(r'chunk_(\d+)\.wav', os.path.basename(filename))
    return int(match.group(1)) if match else -1

# Select device
device = 0 if torch.cuda.is_available() else -1
print(f"[INFO] Using device: {'GPU' if device == 0 else 'CPU'}")

# Load Whisper model (via HuggingFace)
print("[INFO] Loading ASR model...")
asr = pipeline(
    "automatic-speech-recognition",
    model=MODEL_NAME,
    device=device
)
print("[INFO] Model loaded successfully.\n")

# Prepare folders
os.makedirs(TRANSCRIPT_FOLDER, exist_ok=True)

# Load & sort chunk files
audio_files = glob.glob(os.path.join(CHUNK_FOLDER, "chunk_*.wav"))
audio_files.sort(key=extract_number)

if not audio_files:
    print(f"[ERROR] No audio chunk files found in {CHUNK_FOLDER}.")
    exit(1)

print(f"[INFO] Found {len(audio_files)} chunk files.\n")
processed_count = 0

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
    processed_count += 1

    # Batch cleanup every 100 files
    if processed_count % CLEANUP_BATCH == 0:
        print(f"[CLEANUP] Checking last {CLEANUP_BATCH} transcripts for code-switching...")
        txt_files = sorted(glob.glob(os.path.join(TRANSCRIPT_FOLDER, "chunk_*.txt")), key=extract_number)[-CLEANUP_BATCH:]
        removed = 0
        kept = 0

        for txt_file in txt_files:
            with open(txt_file, "r", encoding="utf-8") as f:
                content = f.read()

            if contains_khmer_and_english(content):
                kept += 1
            else:
                audio = os.path.join(CHUNK_FOLDER, os.path.basename(txt_file).replace(".txt", ".wav"))
                os.remove(txt_file)
                if os.path.exists(audio):
                    os.remove(audio)
                removed += 1

        print(f"[CLEANUP REPORT] Kept: {kept}, Removed: {removed}\n")

# ========== [FINAL CLEANUP] ==========
leftover = processed_count % CLEANUP_BATCH
if leftover:
    print(f"[FINAL CLEANUP] Checking last {leftover} transcripts...")
    txt_files = sorted(glob.glob(os.path.join(TRANSCRIPT_FOLDER, "chunk_*.txt")), key=extract_number)[-leftover:]
    removed = 0
    kept = 0

    for txt_file in txt_files:
        with open(txt_file, "r", encoding="utf-8") as f:
            content = f.read()

        if contains_khmer_and_english(content):
            kept += 1
        else:
            audio = os.path.join(CHUNK_FOLDER, os.path.basename(txt_file).replace(".txt", ".wav"))
            os.remove(txt_file)
            if os.path.exists(audio):
                os.remove(audio)
            removed += 1

    print(f"[FINAL CLEANUP REPORT] Kept: {kept}, Removed: {removed}\n")

print("[✅ DONE] All audio files transcribed and filtered.")

import os
import re
import glob

# ========== [CONFIG] ==========
TRANSCRIPT_FOLDER = "data/transcriptions"
CHUNK_FOLDER = "data/chunks"
# ==============================

# Check for Khmer + English (code-switching)
def contains_khmer_and_english(text):
    has_khmer = re.search(r'[\u1780-\u17FF]', text)
    has_english = re.search(r'[A-Za-z]', text)
    return has_khmer and has_english

# Extract number for sorting
def extract_number(filename):
    match = re.search(r'chunk_(\d+)\.txt', os.path.basename(filename))
    return int(match.group(1)) if match else -1

# Load all transcript files
txt_files = sorted(glob.glob(os.path.join(TRANSCRIPT_FOLDER, "chunk_*.txt")), key=extract_number)

if not txt_files:
    print("[ERROR] No transcript files found.")
    exit(1)

print(f"[INFO] Found {len(txt_files)} transcript files to filter.")

removed = 0
kept = 0

for txt_file in txt_files:
    with open(txt_file, "r", encoding="utf-8") as f:
        content = f.read()

    if contains_khmer_and_english(content):
        kept += 1
    else:
        # Remove .txt
        os.remove(txt_file)

        # Remove corresponding .wav
        audio_file = os.path.join(CHUNK_FOLDER, os.path.basename(txt_file).replace(".txt", ".wav"))
        if os.path.exists(audio_file):
            os.remove(audio_file)

        removed += 1

print(f"\n[FINAL REPORT] Kept: {kept}, Removed: {removed}")

import os
import re
import glob
import string
from num2words import num2words  # pip install num2words

transcript_folder = "data/transcriptions"

def clean_transcription(text):
    # Replace all numbers with words
    def replace_number(match):
        try:
            return num2words(int(match.group()), lang='en')
        except:
            return match.group()  # leave unchanged if conversion fails

    text = re.sub(r'\d+', replace_number, text)

    # Allowed characters: English letters, Khmer range, spaces, and some optional Khmer punctuation
    allowed_chars = string.ascii_letters + " " + "។៕"  # You can add more Khmer punctuation if needed

    cleaned_text = ''.join(
        ch for ch in text
        if (('\u1780' <= ch <= '\u17FF') or (ch in allowed_chars) or ch.isspace())
    )

    # Normalize multiple spaces
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

    return cleaned_text

# Process each transcript
txt_files = glob.glob(os.path.join(transcript_folder, "chunk_*.txt"))

for txt_file in txt_files:
    with open(txt_file, "r", encoding="utf-8") as f:
        content = f.read()

    cleaned = clean_transcription(content)

    with open(txt_file, "w", encoding="utf-8") as f:
        f.write(cleaned)

print(f"✅ Cleaned {len(txt_files)} transcripts (special chars removed, numbers converted).")

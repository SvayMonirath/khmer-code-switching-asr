import os
import re
from num2words import num2words

# Convert digits to words (e.g., 123 → "one hundred twenty three")
def convert_numbers_to_words(text):
    def replace_num(match):
        return num2words(int(match.group()))
    return re.sub(r'\d+', replace_num, text)

# Remove punctuation, emojis, symbols — keep only Khmer, English, spaces
def clean_text(text):
    text = convert_numbers_to_words(text)
    return re.sub(r'[^A-Za-z\u1780-\u17FF\s]', '', text)

# Add <km> or <en> tags per segment
def tag_language_segments(text):
    words = text.split()
    tagged_segments = []

    current_lang = None
    segment_words = []

    def flush_segment():
        if not segment_words:
            return
        prefix = '<km>' if current_lang == 'km' else '<en>'
        tagged_segments.append(prefix + ' ' + ' '.join(segment_words))

    for word in words:
        if re.search(r'[\u1780-\u17FF]', word):
            lang = 'km'
        elif re.search(r'[A-Za-z]', word):
            lang = 'en'
        else:
            lang = 'en'  # fallback

        if lang != current_lang:
            flush_segment()
            segment_words = [word]
            current_lang = lang
        else:
            segment_words.append(word)

    flush_segment()
    return ' '.join(tagged_segments)

# Clean *.txt → *.cleaned.txt, then remove the original
def process_cleaning(folder):
    print("=== Cleaning raw transcript files ===")
    for filename in os.listdir(folder):
        if filename.endswith(".txt") and not filename.endswith(".cleaned.txt") and not filename.endswith(".tagged.txt"):
            original_path = os.path.join(folder, filename)
            with open(original_path, "r", encoding="utf-8") as f:
                text = f.read()

            cleaned = clean_text(text)

            cleaned_name = filename.replace(".txt", ".cleaned.txt")
            cleaned_path = os.path.join(folder, cleaned_name)
            with open(cleaned_path, "w", encoding="utf-8") as f:
                f.write(cleaned)

            os.remove(original_path)
            print(f"[CLEANED] {filename} → {cleaned_name} (deleted original)")

# Tag *.cleaned.txt → *.tagged.txt, then remove the cleaned
def process_tagging_and_cleanup(folder):
    print("\n=== Tagging cleaned files and removing them ===")
    for filename in os.listdir(folder):
        if filename.endswith(".cleaned.txt"):
            cleaned_path = os.path.join(folder, filename)
            with open(cleaned_path, "r", encoding="utf-8") as f:
                cleaned = f.read()

            tagged = tag_language_segments(cleaned)
            tagged_name = filename.replace(".cleaned.txt", ".tagged.txt")
            tagged_path = os.path.join(folder, tagged_name)
            with open(tagged_path, "w", encoding="utf-8") as f:
                f.write(tagged)

            os.remove(cleaned_path)
            print(f"[TAGGED] {filename} → {tagged_name} (deleted cleaned)")

def main():
    folder = os.path.join(os.getcwd(), "data", "transcriptions")
    if not os.path.isdir(folder):
        print(f"[ERROR] Folder not found: {folder}")
        return

    process_cleaning(folder)
    process_tagging_and_cleanup(folder)
    print("\n✅ Done tagging all transcriptions.")

if __name__ == "__main__":
    main()

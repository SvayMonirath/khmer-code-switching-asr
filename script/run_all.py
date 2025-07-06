import subprocess

scripts = [
    "python script/download_audio.py",
    "python script/chunk_audio.py",
    "python script/transcribe_and_filter.py",
    "python script/clean_transcripts.py",
    "python script/tag_audio.py"
]

for cmd in scripts:
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"Error: Command failed - {cmd}")
        break
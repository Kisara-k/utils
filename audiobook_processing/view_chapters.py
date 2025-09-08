import subprocess
import sys
import re

def seconds_to_hhmmss(seconds):
    total_seconds = int(float(seconds))
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def list_chapters_ffmpeg(file_path):
    try:
        result = subprocess.run(
            ['ffmpeg', '-i', file_path],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )

        output = result.stderr  # ffmpeg writes info to stderr

        chapter_pattern = re.compile(
            r"Chapter #\d+:\d+: start (\d+\.\d+), end (\d+\.\d+)\n\s+Metadata:\n\s+title\s+:\s(.+)"
        )

        matches = chapter_pattern.findall(output)

        if not matches:
            print("No chapters found.")
            return

        print(f"\nChapters in '{file_path}':\n")
        for start, _, title in matches:
            print(f"{seconds_to_hhmmss(start)} {title}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Drag and drop an .m4b file onto this script to see chapters.")
    else:
        list_chapters_ffmpeg(sys.argv[1])
        input("\nPress Enter to exit...")

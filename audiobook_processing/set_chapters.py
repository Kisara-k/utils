import subprocess
import sys
import os
import re

def format_ffmpeg_time(time_str):
    parts = time_str.strip().split(":")
    while len(parts) < 3:
        parts.insert(0, "00")
    return ":".join(parts)

def hhmmss_to_seconds(time_str):
    h, m, s = [int(t) for t in time_str.strip().split(":")]
    return h * 3600 + m * 60 + s

def seconds_to_hhmmss(seconds):
    total_seconds = int(float(seconds))
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def backup_original_chapters(m4b_file, backup_txt):
    result = subprocess.run(
        ['ffmpeg', '-i', m4b_file],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )
    output = result.stderr
    chapter_pattern = re.compile(
        r"Chapter #\d+:\d+: start (\d+\.\d+), end (\d+\.\d+)\n\s+Metadata:\n\s+title\s+:\s(.+)"
    )
    matches = chapter_pattern.findall(output)

    if not matches:
        print("⚠️  No chapters found to back up.")
        return

    with open(backup_txt, 'w', encoding='utf-8') as f:
        for start, _, title in matches:
            f.write(f"{seconds_to_hhmmss(start)} {title}\n")

    print(f"✅ Original chapters backed up to '{backup_txt}'")

def parse_named_chapter_file(file_path):
    chapters = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            time_str, title = line.strip().split(' ', 1)
            chapters.append((format_ffmpeg_time(time_str), title))
    return chapters

def create_ffmpeg_metadata(chapters, metadata_path):
    with open(metadata_path, 'w', encoding='utf-8') as f:
        f.write(";FFMETADATA1\n")
        for i, (start, title) in enumerate(chapters):
            start_sec = hhmmss_to_seconds(start)
            if i + 1 < len(chapters):
                end_sec = hhmmss_to_seconds(chapters[i + 1][0])
            else:
                end_sec = start_sec + 1  # fallback
            f.write(f"\n[CHAPTER]\nTIMEBASE=1/1\nSTART={start_sec}\nEND={end_sec}\ntitle={title}\n")

def replace_chapters(original_file, metadata_file, output_file):
    subprocess.run([
        'ffmpeg', '-y',
        '-i', original_file,
        '-i', metadata_file,
        '-map', '0',             # all streams from original
        '-map_metadata', '1',    # metadata from second input
        '-map_chapters', '1',    # chapters from metadata
        '-c', 'copy',            # copy streams
        '-f', 'mp4',             # force mp4 container
        output_file
    ])
    print(f"✅ New chapters saved to '{output_file}'")

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1].lower().endswith(".m4b"):
        m4b_path = sys.argv[1]
        chapter_txt = os.path.join(os.getcwd(), "chapters.txt")
        if not os.path.exists(chapter_txt):
            print("⚠️ No 'chapters.txt' found in the current directory.")
            input("Press Enter to exit...")
            sys.exit(1)
    elif len(sys.argv) == 3:
        m4b_path = sys.argv[1]
        chapter_txt = sys.argv[2]
    else:
        print("Usage:")
        print("  python script.py <input.m4b> <chapters.txt>")
        print("  OR just drag & drop an .m4b (must have chapters.txt in same folder)")
        input("Press Enter to exit...")
        sys.exit(1)

    base_name = os.path.splitext(m4b_path)[0]
    metadata_path = base_name + "_chapter_metadata.txt"
    backup_txt = base_name + "_original_chapters.txt"
    output_file = base_name + "_with_new_chapters.m4b"

    backup_original_chapters(m4b_path, backup_txt)
    chapters = parse_named_chapter_file(chapter_txt)
    if len(chapters) < 2:
        print("⚠️ You need at least 2 chapters to define start and end times.")
        input("Press Enter to exit...")
        sys.exit(1)

    create_ffmpeg_metadata(chapters, metadata_path)
    replace_chapters(m4b_path, metadata_path, output_file)

    input("\nDone. Press Enter to exit...")

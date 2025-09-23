import json
import os

def json_to_md(data, max_level=4):
    # Sort hierarchically by headings
    def sort_key(entry):
        return tuple(entry.get(f"h{i+1}", "") for i in range(max_level))

    sorted_data = sorted(data, key=sort_key)
    md_lines = []
    prev_headings = [""] * max_level

    for entry in sorted_data:
        # Print only headings that changed
        for i in range(max_level):
            h = entry.get(f"h{i+1}", "")
            if h and h != prev_headings[i]:
                for j in range(i, max_level):
                    prev_headings[j] = ""
                md_lines.append("#" * (i+1) + " " + h)
                prev_headings[i] = h

        # Add content exactly as in JSON
        content = entry.get("content", "")
        if content:
            md_lines.append(content)

    # Join lines with a single newline
    return "\n".join(md_lines)

if __name__ == "__main__":
    input_file = "output.json"  # replace with your JSON file
    output_file = os.path.splitext(input_file)[0] + "_reconstructed.md"

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    md_text = json_to_md(data)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(md_text)

    print(f"Reconstruction complete. Output saved to {output_file}")

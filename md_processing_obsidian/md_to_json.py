import re
import json

def trim_outer_spaces_keep_newlines(text):
    """
    Trim spaces/newlines outside the outermost newlines that surround non-blank content.
    Keeps the detected newlines at start and end.
    """
    # Search for first and last non-blank character
    match = re.search(r'\S', text)
    if not match:
        return text  # all blank, do nothing

    first_non_blank = match.start()
    last_non_blank = max(i for i, c in enumerate(text) if not c.isspace() == False)

    # Find the first newline before or at the first non-blank character
    start_nl = text.rfind('\n', 0, first_non_blank + 1)
    start_nl = start_nl if start_nl != -1 else 0  # if none, start from 0

    # Find the last newline at or after the last non-blank character
    end_nl = text.find('\n', last_non_blank)
    end_nl = end_nl if end_nl != -1 else len(text) - 1

    # Include the newlines themselves
    return text[start_nl:end_nl + 1]

def md_to_json(md_text, max_level=4):
    heading_pattern = re.compile(r'^(#{1,' + str(max_level) + r'})\s+(.*)')

    results = []
    current = {f"h{i}": "" for i in range(1, max_level + 1)}
    current["content"] = []

    for line in md_text.splitlines():
        match = heading_pattern.match(line)
        if match:
            if current["content"]:
                content_text = "\n".join(current["content"])
                trimmed = trim_outer_spaces_keep_newlines(content_text)
                results.append({**{f"h{i}": current[f"h{i}"] for i in range(1, max_level + 1)},
                                "content": trimmed})
                current["content"] = []

            level = len(match.group(1))
            heading_text = match.group(2).strip()

            for i in range(1, max_level + 1):
                if i == level:
                    current[f"h{i}"] = heading_text
                elif i > level:
                    current[f"h{i}"] = ""
        else:
            current["content"].append(line)

    if current["content"]:
        content_text = "\n".join(current["content"])
        trimmed = trim_outer_spaces_keep_newlines(content_text)
        results.append({**{f"h{i}": current[f"h{i}"] for i in range(1, max_level + 1)},
                        "content": trimmed})

    return results

if __name__ == "__main__":
    with open("Hamza.md", "r", encoding="utf-8") as f:
        md_text = f.read()

    structured_data = md_to_json(md_text)

    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(structured_data, f, indent=4, ensure_ascii=False)

    print("Extraction complete. Output saved to output.json")

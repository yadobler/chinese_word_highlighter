import gzip
import json

def parse_cedict_line(line):
    """Parses a single line of CC-CEDICT and extracts simplified, pinyin, and meaning."""
    if not line or line.startswith("#"):
        return None

    parts = line.rstrip("/\n").split("/")
    if len(parts) < 2:
        return None

    english = "/".join(parts[1:])  # Join in case there are multiple meanings
    char_pinyin = parts[0].split("[")

    characters = char_pinyin[0].split()
    if len(characters) < 2:
        return None  # Ignore invalid lines

    simplified = characters[1]  # Second item is the simplified form
    pinyin = char_pinyin[1].rstrip("]") if len(char_pinyin) > 1 else ""

    return {"simplified": simplified, "pinyin": pinyin, "meaning": english}

def preprocess_cedict(input_file, output_file):
    dictionary = {}
    
    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            entry = parse_cedict_line(line)
            if entry:
                simplified = entry["simplified"]
                if simplified not in dictionary:
                    dictionary[simplified] = []
                dictionary[simplified].append({
                    "pinyin": entry["pinyin"],
                    "meaning": entry["meaning"]
                })

    # Compress and save as a JSON file
    with gzip.open(output_file, "wt", encoding="utf-8") as gz:
        json.dump(dictionary, gz, ensure_ascii=False)

if __name__ == "__main__":
    preprocess_cedict("./cedict_ts.u8", "./cedict.json.gz")


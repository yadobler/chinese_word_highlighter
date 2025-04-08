import gzip
import json
import re

# Pinyin tone conversion
PinyinToneMark = {
    0: "aoeiuvü",
    1: "āōēīūǖǖ",
    2: "áóéíúǘǘ",
    3: "ǎǒěǐǔǚǚ",
    4: "àòèìùǜǜ",
}

def decode_pinyin(s):
    """Converts numbered Pinyin to tone-marked Pinyin and appends the tone number back."""
    s = s.replace(" : ", " ").lower()
    r = ""
    t = ""
    tone_number = "0"

    for c in s:
        if c.isalpha():
            t += c
        elif c == ':':
            assert t[-1] == 'u'
            t = t[:-1] + "ü"
        else:
            if c.isdigit() and '0' <= c <= '5':
                tone = int(c) % 5
                tone_number = c  # Store the tone number
                if tone != 0:
                    m = re.search("[aoeiuvü]+", t)
                    if m:
                        vowel_seq = m.group(0)
                        index = PinyinToneMark[0].index(vowel_seq[0])  # Get first vowel match
                        t = t[:m.start(0)] + PinyinToneMark[tone][index] + t[m.end(0):]
            r += t + tone_number  # Append tone number
            t = ""
            tone_number = "0"  # Reset tone number

    r += t
    return r

def parse_cedict_line(line):
    """Parses a CC-CEDICT line and extracts simplified, Pinyin, and meanings."""
    if not line or line.startswith("#"):
        return None

    parts = line.rstrip("/\n").split("/")
    if len(parts) < 2:
        return None

    english = "; ".join(parts[1:])  # Join meanings
    char_and_pinyin = parts[0].split("[")
    characters = char_and_pinyin[0].split()

    if len(characters) < 2:
        return None  # Ignore invalid lines

    simplified = characters[1]
    raw_pinyin = char_and_pinyin[1].rstrip("]")

    return {
        "simplified": simplified,
        "pinyin": decode_pinyin(raw_pinyin),
        "meaning": english
    }

def preprocess_cedict(input_file, output_file):
    """Processes CC-CEDICT, groups entries by character, and compresses output."""
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
        json.dump(dictionary, gz, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    preprocess_cedict("./cedict_ts.u8", "../public/cedict.json.gz")

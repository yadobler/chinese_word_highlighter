import gzip
import json
import re

# https://stackoverflow.com/questions/8200349/convert-numbered-pinyin-to-pinyin-with-tone-marks
PinyinToneMark = {
    0: "aoeiuv\u00fc",
    1: "\u0101\u014d\u0113\u012b\u016b\u01d6\u01d6",
    2: "\u00e1\u00f3\u00e9\u00ed\u00fa\u01d8\u01d8",
    3: "\u01ce\u01d2\u011b\u01d0\u01d4\u01da\u01da",
    4: "\u00e0\u00f2\u00e8\u00ec\u00f9\u01dc\u01dc",
}

def decode_pinyin(s):
    s = s.replace(" : ", " ").lower()
    r = ""
    t = ""
    for c in s:
        if c >= 'a' and c <= 'z':
            t += c
        elif c == ':':
            assert t[-1] == 'u'
            t = t[:-1] + "\u00fc"
        else:
            if c >= '0' and c <= '5':
                tone = int(c) % 5
                if tone != 0:
                    m = re.search("[aoeiuv\u00fc]+", t)
                    if m is None:
                        t += c
                    elif len(m.group(0)) == 1:
                        t = t[:m.start(0)] + PinyinToneMark[tone][PinyinToneMark[0].index(m.group(0))] + t[m.end(0):]
                    else:
                        if 'a' in t:
                            t = t.replace("a", PinyinToneMark[tone][0])
                        elif 'o' in t:
                            t = t.replace("o", PinyinToneMark[tone][1])
                        elif 'e' in t:
                            t = t.replace("e", PinyinToneMark[tone][2])
                        elif t.endswith("ui"):
                            t = t.replace("i", PinyinToneMark[tone][3])
                        elif t.endswith("iu"):
                            t = t.replace("u", PinyinToneMark[tone][4])
                        else:
                            t += "!"
            r += t
            t = ""
    r += t
    return r

def parse_cedict_line(line):
    """Parses a single line of CC-CEDICT and extracts simplified, pinyin, and meaning."""
    if not line or line.startswith("#"):
        return None

    parts = line.rstrip("/\n").split("/")
    if len(parts) < 2:
        return None

    english = "; ".join(parts[1:])  # Join in case there are multiple meanings
    
    char_and_pinyin = parts[0].split('[')
    characters = char_and_pinyin[0]
    characters = characters.split()
    simplified = characters[1]
    pinyin = char_and_pinyin[1]
    pinyin = pinyin.rstrip()
    pinyin = pinyin.rstrip("]")
    if len(characters) < 2:
        return None  # Ignore invalid lines

    return {"simplified": simplified, "pinyin": decode_pinyin(pinyin), "meaning": english}

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
    preprocess_cedict("./cedict_ts.u8", "../public/cedict.json.gz")


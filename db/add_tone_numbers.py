import csv

PinyinToneMark = {
    5: ["a","o","e","i","u","v","\u00fc"],
    1: ["\u0101","\u014d","\u0113","\u012b","\u016b","\u01d6","\u01d6"],
    2: ["\u00e1","\u00f3","\u00e9","\u00ed","\u00fa","\u01d8","\u01d8"],
    3: ["\u01ce","\u01d2","\u011b","\u01d0","\u01d4","\u01da","\u01da"],
    4: ["\u00e0","\u00f2","\u00e8","\u00ec","\u00f9","\u01dc","\u01dc"],
}

results = []
with open("./default_values_pre.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        pinyins = []
        for pinyin in row["Pinyin"].split(" "):
            for i in range(1,6):
                test = sum([1 if c in PinyinToneMark[i] else 0 for c in pinyin])
                if test > 0:
                    pinyin += str(i)
                    pinyins.append(pinyin)
                    break
        row["Pinyin"] = " ".join(pinyins)
        results.append(row)

results.sort(key=lambda x: int(x["Chapter"]) if x["Chapter"] else 0)
with open("../public/default_values.csv", "w") as f:
    writer = csv.DictWriter(f, ["Simplified","Chapter","Pinyin","Category","Meaning"])
    writer.writerows(results)

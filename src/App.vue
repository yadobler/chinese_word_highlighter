<script setup lang="ts">
    import { ref, onMounted } from 'vue';
import Papa from 'papaparse';

// --- Types ---
type ProcessedSegment = {
  text: string;
  type: 'found' | 'not-found' | 'unknown';
  data?: {
    chapter?: string;
    pinyin: string;
    category?: string;
    meaning: string;
  }[];
};

type Dictionary = Record<string, { 
  pinyin: string; 
  meaning: string; 
}[]>;

type CsvDictionary = Record<string, { 
  chapter: string;
  pinyin: string;
  category: string;
  meaning: string;
}[]>;

type UnknownWord = {
  index: number;
  word: string;
  pinyin?: string;
  meaning?: string;
};

// --- State ---
const csvInput = ref('');
const scriptInput = ref('');

const ccCedict = ref<Dictionary>({});
const csvDictionary = ref<CsvDictionary>({});
const processedOutput = ref<ProcessedSegment[]>([]);

const selectedSegmentDetails = ref<ProcessedSegment | null>(null);
const unknownWords = ref<UnknownWord[]>([]);

// --- Lifecycle ---
onMounted(async () => {
  try {
    // Load default CSV dictionary
    const csvResponse = await fetch('/chinese_word_highligher/default_values.csv');
    if (!csvResponse.ok) throw new Error("Failed to load CSV dictionary.");
    csvInput.value = await csvResponse.text();
    parseCsvData();

    // Load and decompress CC-CEDICT
    const dictResponse = await fetch('/chinese_word_highligher/cedict.json.gz');
    if (!dictResponse.ok) throw new Error("Failed to load CC-CEDICT.");
    ccCedict.value = JSON.parse(await dictResponse.text());

  } catch (error) {
    console.error("Error loading dictionaries:", error);
  }
});

// --- Parse CSV Dictionary ---
const parseCsvData = () => {
  console.log("Parsing CSV data...");

  const result = Papa.parse(csvInput.value.trim(), {
    header: true, 
    skipEmptyLines: true
  });

  const parsedData = result.data as Record<string, string>[];
  const newDictionary: CsvDictionary = {};

parsedData.forEach((entry_raw) => {
  const simplified = entry_raw["Simplified"];
  if (simplified) {
    const entry = {
      chapter: entry_raw["Chapter"]?.trim() || "",
      pinyin: entry_raw["Pinyin"]?.trim() || "",
      category: entry_raw["Category"]?.trim() || "",
      meaning: entry_raw["Meaning"]?.trim() || ""
    };

    if (!newDictionary[simplified]) {
      newDictionary[simplified] = [];
    }
    newDictionary[simplified].push(entry);
  }
});

  csvDictionary.value = newDictionary;
  console.log("CSV Dictionary populated:", csvDictionary.value);
};

// --- Process Script ---
const processScript = () => {
  if (!Object.keys(ccCedict.value).length) {
    console.warn("CC-CEDICT is empty. Cannot process script.");
    processedOutput.value.push({ text: 'Error: Dictionary not loaded or empty.', type: 'not-found' });
    return;
  }

  const scriptText = scriptInput.value;
  const cedictWords = Object.keys(ccCedict.value).sort((a, b) => b.length - a.length); // Sort longest first
  const results: ProcessedSegment[] = [];
  const unknownSet = new Set<string>();
  let i = 0;

  while (i < scriptText.length) {
    let matchFound = false;
    // if (!scriptText[i].trim()) {
    //   i += 1;
    //   continue;
    // }

    for (const word of cedictWords) {
      if (scriptText.startsWith(word, i)) {
        matchFound = true;
        const inCsv = !!csvDictionary.value[word];

        results.push({
          text: word,
          type: inCsv ? 'found' : 'not-found',
          data: inCsv ? csvDictionary.value[word] : ccCedict.value[word]
        });

        if (!inCsv) unknownSet.add(word); // Collect "not-found" words
        i += word.length;
        break;
      }
    }

    if (!matchFound) {
      for (const word in csvDictionary.value) {
        if (scriptText.startsWith(word, i)) {
          results.push({
            text: word,
            type: 'found',
            data: csvDictionary.value[word]
          });
          i += word.length;
          matchFound = true;
          break;
        }
      }
    }

    if (!matchFound) {
      i += 1; // Move to the next character
    }
  }

  processedOutput.value = results;

  unknownWords.value = Array.from(unknownSet).map((word, index) => ({
    index: index + 1,
    word: word,
    pinyin: ccCedict.value[word]?.[0]?.pinyin || "",
    meaning: ccCedict.value[word]?.[0]?.meaning || ""
  }));
};

// --- Show Details ---
const showDetails = (segment: ProcessedSegment) => {
  if (segment.type === 'found' && segment.data?.length) {
    selectedSegmentDetails.value = segment;
  }
};

</script>

<template>
    <div class="app-container">
        <h1>Chinese Word Highlighter</h1>

        <div class="input-area">
            <div class="textarea-container">
                <label for="csvInput">Dictionary</label>
                <textarea id="csvInput" v-model="csvInput" rows="10" placeholder="Paste CSV data..." @change="parseCsvData"></textarea>
            </div>
            <div class="textarea-container">
                <label for="scriptInput">Script Text</label>
                <textarea id="scriptInput" v-model="scriptInput" rows="10" placeholder="Paste text..."></textarea>
            </div>
        </div>

        <button @click="processScript" class="process-button">Process Script</button>

        <div class="output-container">
            <div class="output-display">
                <span v-for="(segment, index) in processedOutput" 
                      :key="index" 
                      :class="segment.type" 
                      @click="showDetails(segment)">
                    {{ segment.text }}
                </span>
            </div>

            <div v-if="selectedSegmentDetails?.data" class="details-box">
                <div v-for="(entry, idx) in selectedSegmentDetails.data" :key="idx">
                    <div><strong>Pinyin:</strong> {{ entry.pinyin }}</div>
                    <div><strong>Meaning:</strong> {{ entry.meaning }}</div>
                    <hr v-if="idx < selectedSegmentDetails.data.length - 1">
                </div>
            </div>
        </div>

        <div v-if="unknownWords.length > 0" class="unknown-words-table">
            <h2>Not Found Words</h2>
            <table>
                <thead>
                    <tr>
                        <th>Index</th>
                        <th>Word</th>
                        <th>Pinyin</th>
                        <th>Meaning</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="word in unknownWords" :key="word.index">
                        <td>{{ word.index }}</td>
                        <td>{{ word.word }}</td>
                        <td>{{ word.pinyin }}</td>
                        <td>{{ word.meaning }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>

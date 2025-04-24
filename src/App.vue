<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { ungzip } from 'pako'
import Papa from 'papaparse';

// --- Types ---
type RawSegment = { 
    pinyin: string[];
    tones: number[];
    meaning: string;
    chapter?: string;
    category?: string;
};

type ProcessedSegment = {
    text: string;
    type: 'found' | 'not-found' | 'unknown';
    data?: RawSegment[];
}


// --- State ---
const csvInput = ref('');
const scriptInput = ref('');

const ccCedict = ref<Record<string, RawSegment[]>>({});
const csvDictionary = ref<Record<string, RawSegment[]>>({});

const processedOutput = ref<ProcessedSegment[]>([]);
const newWords = ref<ProcessedSegment[]>([]);

const selectedSegmentDetails = ref<ProcessedSegment | null>(null);

const clearCsv = () => {
    csvInput.value = '';
};

// --- Functions ---
async function loadDefaultCsv() {
  const basePath = '/chinese_word_highlighter/default_values';
  const selectedFiles: string[] = [];

  if ((document.getElementById('use_punctuations') as HTMLInputElement).checked) {
    selectedFiles.push(`${basePath}.csv`);
  }
  if ((document.getElementById('use_ch1_7') as HTMLInputElement).checked) {
    selectedFiles.push(`${basePath}_1.csv`);
  }
  if ((document.getElementById('use_ch8_14') as HTMLInputElement).checked) {
    selectedFiles.push(`${basePath}_2.csv`);
  }
  if ((document.getElementById('use_ch15_20') as HTMLInputElement).checked) {
    selectedFiles.push(`${basePath}_3.csv`);
  }
  if ((document.getElementById('use_ch21_26') as HTMLInputElement).checked) {
    selectedFiles.push(`${basePath}_4.csv`);
  }

  csvInput.value = "Simplified,Chapter,Pinyin,Category,Meaning\n";
  for (const file of selectedFiles) {
    console.log(file);
    const response = await fetch(file);
    const text = await response.text();
    csvInput.value += text;
  }
}

async function importCsv() {
    try {
        // Create an invisible file input element
        const input = document.createElement("input");
        input.type = "file";
        input.accept = ".csv, text/csv";
        
        // Wait for the user to select a file
        input.addEventListener("change", async (event) => {
            const target = event.target as HTMLInputElement;
            if (!target.files || target.files.length === 0) {
                alert("No file selected.");
                return;
            }

            const file = target.files[0];
            const reader = new FileReader();

            reader.onload = (e) => {
                csvInput.value = e.target?.result?.toString() || "";
            };

            reader.readAsText(file);
        });

        // Trigger the file selection dialog
        input.click();
    } catch (error) {
        alert("Error selecting or parsing CSV:\n" + error);
    }
};

function getToneNumber(pinyin_tones: string) : { pinyin: string[], tones: number[] } {

    const pinyin_segments = pinyin_tones.split(" ");
    
    const tones = Array(0);
    const pinyin = Array(0);

    pinyin_segments.forEach((word) => {
        const match = word.match('([^\d]*)([0-5])')
        if (match) {
            tones.push(Number.parseInt(match[2]))
            pinyin.push(match[1])
        } else {
            tones.push(5)
            pinyin.push(word)
        }
    })
    return {pinyin: pinyin, tones: tones};
}

// --- Parse CSV Dictionary ---
function parseCsvData() {
    console.log("Parsing CSV data...");
    csvDictionary.value = {}

    const result = Papa.parse(csvInput.value.trim(), {
        header: true, 
        skipEmptyLines: true
    });

    const parsedData = result.data as Record<string, string>[];
    const newDictionary: Record<string, RawSegment[]> = {};

    parsedData.forEach((entry_raw) => {
        const simplified = entry_raw["Simplified"];
        if (simplified) {
            const pinyin_tones = getToneNumber(entry_raw["Pinyin"]);
            const entry = {
                chapter: entry_raw["Chapter"].trim(),
                pinyin: pinyin_tones["pinyin"],
                category: entry_raw["Category"].trim(),
                meaning: entry_raw["Meaning"].trim(),
                tones: pinyin_tones["tones"]
            };

            if (!newDictionary[simplified]) {
                newDictionary[simplified] = [];
            };
            newDictionary[simplified].push(entry);
        }
    });

    csvDictionary.value = newDictionary;
    console.log("CSV Dictionary populated:", csvDictionary.value);
};

// --- Process Script ---
async function processScript() {
    if (!Object.keys(ccCedict.value).length) {
        console.warn("CC-CEDICT is empty. Cannot process script.");
        processedOutput.value.push({ text: 'Error: Dictionary not loaded or empty.', type: 'not-found' });
        return;
    }

    parseCsvData();

    const scriptText = scriptInput.value;
    const cedictWords = Object.keys(ccCedict.value).sort((a, b) => b.length - a.length); // Sort longest first
    const results: ProcessedSegment[] = [];
    const newWordsSet = new Set<string>();

    function GetPhrasesInCsv(word: string): string[] | null {
        if (csvDictionary.value[word]?.[0]) return [word]; // Direct match

        // Generate all possible segmentations
        const validSegments: string[] = [];
        for (let i = 1; i < word.length; i++) {
            const left = word.substring(0, i);
            const right = word.substring(i);

            if (csvDictionary.value[left] && csvDictionary.value[right]) {
                validSegments.push(left, right);
                return validSegments;
            }
        }
        return null; // No valid segmentation found
    }

    let i = 0;
    while (i < scriptText.length) {
        if (scriptText[i] == '\n') {
            results.push({ text: '\n', type: 'unknown' });
            i += 1
            continue;
        }

        if (scriptText[i].match(/[a-z]/i)) {
            results.push({ 
                text: scriptText[i], 
                type: 'found',
                data: [{
                    pinyin: [scriptText[i]],
                    meaning: scriptText[i],
                    tones: Array(1).fill(5),
                }], 
            });
            i += 1
            continue;
        }

        if (!scriptText[i].trim()) {
            i += 1;
            continue;
        }

        let matchFound = false;
        for (const word of cedictWords) {
            if (scriptText.startsWith(word, i)) {
                matchFound = true;
                const ValidPhrases = GetPhrasesInCsv(word);

                if (ValidPhrases) {
                    // Push each segment separately
                    for (const phrase of ValidPhrases) {
                        results.push({
                            text: phrase,
                            type: 'found',
                            data: [{
                                pinyin: csvDictionary.value[phrase]?.[0].pinyin,
                                tones: csvDictionary.value[phrase]?.[0].tones,
                                meaning: csvDictionary.value[phrase]?.[0].meaning,
                                chapter: csvDictionary.value[phrase]?.[0].chapter,
                                category: csvDictionary.value[phrase]?.[0].category
                            }]
                        });
                    }
                } else {
                    results.push({
                        text: word,
                        type: 'not-found',
                        data: ccCedict.value[word]
                    });
                    newWordsSet.add(word); // Collect "not-found" words
                }

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
    newWords.value =  Array.from(newWordsSet).map((word: string) => ({
        text: word,
        type: 'not-found',
        data: ccCedict.value[word] || [{
            tones: Array(word.length).fill(5),
            pinyin: "",
            meaning: ""
        }]
    }));
};

// --- Show Details ---
const showDetails = (segment: ProcessedSegment) => {
    if (segment.type === 'found' && segment.data?.length) {
        selectedSegmentDetails.value = segment;
    }
};

// --- Lifecycle ---
onMounted(async () => {
    try {
        // Load and decompress CC-CEDICT
        const dictResponse = await fetch('/chinese_word_highlighter/cedict.json.gz');
        if (!dictResponse.ok) throw new Error("Failed to load CC-CEDICT.");
        const compressedData = await dictResponse.arrayBuffer();
        const decompressedData = ungzip(new Uint8Array(compressedData));
        ccCedict.value = JSON.parse(new TextDecoder().decode(decompressedData));
    } catch (error) {
        console.error("Error loading dictionaries:", error, "\nTrying backup");
        try {
            // try 2
            // Load and decompress CC-CEDICT
            const dictResponse = await fetch('/chinese_word_highlighter/cedict.json.gz');
            if (!dictResponse.ok) throw new Error("Failed to load CC-CEDICT.");
            ccCedict.value = JSON.parse(await dictResponse.text());
        } catch (error) {
            console.error("Error loading dictionaries (backup):", error);
        }
    }

    // Load default CSV dictionary
    await loadDefaultCsv();

});

</script>

<template>
    <div class="app-container">
        <h1>Chinese Word Highlighter</h1>

        <!-- Input -->
        <div class="input-area">
            <div class="textarea-container">
                <label for="csvInput">Dictionary</label>
                <textarea id="csvInput" v-model="csvInput" rows="10" placeholder="Default CSV data is loading..."
                    @change="parseCsvData"></textarea>
            </div>
            <div class="textarea-container">
                <label for="scriptInput">Script Text</label>
                <textarea id="scriptInput" v-model="scriptInput" rows="10" placeholder="Paste text..."></textarea>
            </div>
        </div>

        <!-- Button -->
        <div class="checkbox-group">
            <input type="checkbox" id="use_punctuations" checked> Punctuations<br>
            <input type="checkbox" id="use_ch1_7" checked> Chapters 1–7<br>
            <input type="checkbox" id="use_ch8_14" checked> Chapters 8–14<br>
            <input type="checkbox" id="use_ch15_20" checked> Chapters 15–20<br>
            <input type="checkbox" id="use_ch21_26" checked> Chapters 21–26<br>
        </div>
        <div class="button-panel">
            <button @click="clearCsv">Clear CSV Input</button>
            <button @click="importCsv">Import CSV from file</button>
            <button @click="processScript">Process Script</button>
        </div>

        <!-- Output -->
        <div class="output-container">

            <!-- normal Highlighted text -->
            <div v-if="processedOutput.length > 0" class="output-display">
                <template v-for="(segment, index) in processedOutput" :key="index">
                    <span v-if="segment.text !== '\n'" :class="segment.type" @click="showDetails(segment)">
                        {{ segment.text }}
                    </span>
                    <br v-else> <!-- Insert <br> for newlines -->
                </template>
            </div>

            <!-- Info -->
            <div v-if="selectedSegmentDetails?.data" class="details-box">
                <div>
                    <h3>{{ selectedSegmentDetails?.text }}</h3>
                </div>
                <div v-for="(entry, idx) in selectedSegmentDetails?.data" :key="idx">
                    <div><strong>Pinyin: </strong> 
                            <template v-for="(tone, i) in entry.tones" :key="i">
                                <span :class="'tone-' + tone">
                                    {{ entry.pinyin[i] }}
                                    <span> </span>
                                </span>
                            </template>
                    </div>
                    <div><strong>Chapter:</strong> {{ entry.chapter }}</div>
                    <div><strong>Category:</strong> {{ entry.category }}</div>
                    <div><strong>Meaning:</strong> {{ entry.meaning }}</div>
                    <hr v-if="idx < selectedSegmentDetails?.data.length - 1">
                </div>
            </div>

            <!-- Annotated Output -->
            <div v-if="processedOutput.length > 0" class="output-container">
                <label for="output-annotated">Annotated</label>
                <div class="output-annotated">
                    <template v-for="(segment, segmentIndex) in processedOutput" :key="segmentIndex">
                        <br v-if="segment.text === '\n'">
                        <span v-else-if="segment.text !== '\n'">
                            <template v-if="segment.data && segment.data.length">
                                <ruby v-for="(char, i) in segment.text.split('')" 
                                    :key="i" 
                                    :class="'tone-' + segment.data[0].tones[i]"> 
                                    {{ char }}
                                    <rt>{{ segment.data[0].pinyin[i] }}</rt> 
                                </ruby>
                            </template>
                            <template v-else>
                                <span>{{ segment.text }}</span>
                            </template>
                            <span>|</span>
                        </span>
                        <span v-else>{{ segment.text }}</span>
                    </template>
                </div>
            </div>

        </div>


        <!-- New Words List -->
        <div v-if="newWords.length > 0" class="new-words-container">
                <label>New Words List</label>
            <br>
            <br>
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
                    <tr v-for="(word, index) in newWords" :key="index">
                        <td>{{ index + 1 }}</td>
                        <td>
                            <template v-for="(tone, i) in word.data?.[0].tones" :key="i">
                                <span :class="'tone-' + tone">
                                    {{ word.text.substring(i, i + 1) }}
                                </span>
                            </template>
                        </td>
                        <td>
                            <template v-for="(tone, i) in word.data?.[0].tones" :key="i">
                                <span :class="'tone-' + tone">
                                    {{ word.data?.[0].pinyin[i]}} 
                                    <span> </span>
                                </span>
                            </template>
                        </td>
                        <td>{{ word.data?.[0].meaning }}</td>
                    </tr>
                </tbody>
            </table>
        </div>

    </div>
</template>

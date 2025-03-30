<script setup lang="ts">
import { ref, onMounted } from 'vue';

// --- State ---
const csvInput = ref('');
const scriptInput = ref('');
const dictionary = ref({});
const processedOutput = ref([]);
const selectedSegmentDetails = ref(null);

// --- Lifecycle ---
onMounted(async () => {
  try {
    const response = await fetch('/default_values.csv');
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    csvInput.value = await response.text();
    parseCsvData();
  } catch (error) {
    console.error("Error fetching default CSV:", error);
    csvInput.value = "Error loading default dictionary. Enter values in this format:\nCharacters, Pinyin, Category, Meaning";
  }
});

// --- Core Logic Functions ---
const parseCsvData = () => {
// --- Placeholder: CSV Parsing Logic ---
// 1. Get text from csvInput.value
// 2. Split into lines. Handle potential '\r\n' or '\n'.
// 3. Ignore empty lines or header (or process header).
// 4. For each line:
//    a. Split by comma. Be mindful of commas within quoted fields if applicable.
//       A simple split(',') might work if meanings don't contain commas.
//       Otherwise, use a more robust CSV parsing approach.
//    b. Extract Simplified, Pinyin, Category, Meaning. Trim whitespace.
//    c. Store in the `dictionary` ref. Using the Simplified form as the key is common.
// Example structure: dictionary.value = { '你好': { pinyin: 'nǐ hǎo', category: 'Idiometic Expression', meaning: 'Hello' }, ... }
// ----
console.log("Parsing CSV data...");
  const lines = csvInput.value.trim().split(/\r?\n/);
  const newDictionary = {};

  if (lines.length > 1) {
    for (let i = 1; i < lines.length; i++) {
      const line = lines[i];
      const parts = [];
      let currentPart = "";
      let inQuotes = false;

      for (const char of line) {
        if (char === '"') {
          inQuotes = !inQuotes;
        } else if (char === ',' && !inQuotes) {
          parts.push(currentPart.trim());
          currentPart = "";
        } else {
          currentPart += char;
        }
      }
      parts.push(currentPart.trim()); // Add the last part

      if (parts.length === 5) {
        const simplified = parts[0].trim();
        if (simplified) {
          newDictionary[simplified] = {
            chapter: parts[1].trim(),
            pinyin: parts[2].trim(),
            category: parts[3].trim(),
            meaning: parts[4].trim().replace(/^"|"$/g, ''), // Basic quote removal
          };
        }
      } else {
        console.warn(`Skipping malformed CSV line ${i + 1}: ${lines[i]}`);
      }
    }
  }

  dictionary.value = newDictionary;
  console.log("Dictionary populated:", dictionary.value);
  // ---- End Placeholder ----
};

const processScript = () => {
  if (Object.keys(dictionary.value).length === 0) {
    console.warn("Dictionary is empty. Cannot process script.");
    processedOutput.value = [{ text: 'Error: Dictionary not loaded or empty.', type: 'not-found'}];
    return;
  }
  
  const scriptText = scriptInput.value;
  const knownWords = Object.keys(dictionary.value).sort((a, b) => b.length - a.length);
  const results = [];
  let i = 0;

  while (i < scriptText.length) {
    let matchFound = false;
    for (const word of knownWords) {
      if (scriptText.startsWith(word, i)) {
        results.push({ text: word, type: 'found', data: dictionary.value[word] });
        i += word.length;
        matchFound = true;
        break;
      }
    }
    if (!matchFound) {
      if (results.length > 0 && results[results.length - 1].type === 'not-found') {
        results[results.length - 1].text += scriptText[i];
      } else {
        results.push({ text: scriptText[i], type: 'not-found' });
      }
      i += 1;
    }
  }
  processedOutput.value = results;
};

const showDetails = (segment) => {
  if (segment.type === 'found' && segment.data) {
    selectedSegmentDetails.value = segment; // Always update the details box
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

      <div v-if="selectedSegmentDetails" class="details-box">
          <div><strong>Chapter:</strong> {{ selectedSegmentDetails.data.chapter }}</div>
          <div><strong>Pinyin:</strong> {{ selectedSegmentDetails.data.pinyin }}</div>
          <div><strong>Category:</strong> {{ selectedSegmentDetails.data.category }}</div>
          <div><strong>Meaning:</strong> {{ selectedSegmentDetails.data.meaning }}</div>
      </div>
  </div>
</div>
</template>

<style scoped>
.app-container {
  font-family: sans-serif;
  max-width: 1200px;
  margin: 20px auto;
  padding: 15px;
  border: 1px solid #ccc;
  border-radius: 8px;
  background-color: #f9f9f9;
}

h1, h2 {
  text-align: center;
  color: #333
}

.input-area {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 20px;
}

.textarea-container {
  flex: 1;
  display: flex;
  flex-direction: column;
}

label {
    margin-bottom: 5px;
    font-weight: bold;
    color: #555;
}

textarea {
    width: 100%; /* Fill container */
    box-sizing: border-box; /* Include padding and border in width */
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 0.9em;
}

.process-button {
    display: block;
    margin: 0 auto 20px auto; /* Center button */
    padding: 10px 25px;
    font-size: 1.1em;
    cursor: pointer;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 5px;
    transition: background-color 0.2s ease;
}

.process-button:hover {
    background-color: #0056b3;
}

.output-container {
  display: flex;
  gap: 20px; /* Space between output and details */
  margin-top: 20px;
  flex-wrap: wrap; /* Allows wrapping on small screens */
}

.output-display, .details-box {
  flex: 1; /* Each takes equal space */
  min-width: 300px; /* Prevents boxes from shrinking too much */
}

.details-box {
  color: black;
  border: 1px solid #ddd;
  background-color: #f4f4f4;
  padding: 15px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Courier New', Courier, monospace;
  min-height: 100px;
  border-radius: 4px;
}

.found {
  color: black;
  border: 1px solid #aaa;
}

.found:hover {
    background-color: #aaa;
}

.not-found {
  color: red;
}
</style>

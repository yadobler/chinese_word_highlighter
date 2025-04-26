# words_in_wordlist

A quick project I threw together with some vibe coding, courtesy of Gemini 2.5 pro experimental, in like an hour. Then I spend the next few weeks with gemini and chatgpt debugging this :) thanks to both for being a friend and therapist when needed. 

This is actually for my Chinese exam, because we all know the programmer's way of dealing with an issue is not to actually deal with it, but to waste 5x time trying to automate it.

## LinkedIn post explanation

(っ◔◡◔)っ *start of overly LinkedIn tone*

**"When 'work smarter, not harder' accidentally means 'work 10x harder'..."**

For my Chinese 4 project, I was supposed to:

- Highlight words from my script
- Make a New Words list manually

A normal person: just highlights and finishes in an hour.

Me: spends days building a full app instead.

Introducing: Chinese Word Highlighter —
because why do something manually when you can dramatically over-engineer it?

Features:
✅ Upload your vocabulary CSV and auto-match words in any script
✅ Annotate characters with tones, pinyin, and definitions
✅ Click to toggle multiple readings (还 can flip from hái to huán!)
✅ Insert a space if words aren't splitting the way you want (东 西 instead of 东西)
✅ Auto-generate a New Words table, ready to paste into your homework

Might've been "extra" but hey — now it's an actual tool I (and maybe others?) can reuse!

Built with Vue.js, caffeine, and questionable time management skills.

## Credits

- CC-Cedict https://www.mdbg.net/chinese/dictionary?page=cedict
- ChatGPT 4
- Gemini 2.5 Pro
- New Practical Chinese Reader textbook

## Recommended IDE Setup

[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur).

But you know, I just use [neovim](https://github.com/yadobler/nixvim-config) MUAHAHAHHAHAAHHAHAHA (click for my config).

## Type Support for `.vue` Imports in TS

TypeScript cannot handle type information for `.vue` imports by default, so we replace the `tsc` CLI with `vue-tsc` for type checking. In editors, we need [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) to make the TypeScript language service aware of `.vue` types.

## Customize configuration

See [Vite Configuration Reference](https://vite.dev/config/).

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Type-Check, Compile and Minify for Production

```sh
npm run build
```

### Lint with [ESLint](https://eslint.org/)

```sh
npm run lint
```

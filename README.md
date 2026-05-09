# 🎓 CLI Teacher — AI-Powered Programming Tutor

> An interactive, terminal-based programming tutor powered by Anthropic's Claude.  
> Learn any language, get quizzed, solve challenges, review code, and track your progress — all from the command line.

---

## Table of Contents

1. [Features](#features)
2. [Supported Languages](#supported-languages)
3. [Learning Modes](#learning-modes)
4. [Requirements](#requirements)
5. [Installation](#installation)
6. [Configuration](#configuration)
7. [Usage](#usage)
8. [In-Session Commands](#in-session-commands)
9. [Progress Tracking](#progress-tracking)
10. [Session Transcripts](#session-transcripts)
11. [Project Structure](#project-structure)
12. [How It Works](#how-it-works)
13. [Improvements Over v1](#improvements-over-v1)
14. [Troubleshooting](#troubleshooting)
15. [Contributing](#contributing)
16. [License](#license)

---

## Features

| Feature | Description |
|---|---|
| 🤖 AI Tutor | Powered by Claude — adapts explanations to your experience level |
| 📚 8 Learning Modes | Lessons, quizzes, challenges, code review, debug helper, cheat sheets, roadmaps, and free chat |
| 🌍 19+ Languages | Python, Rust, Go, TypeScript, JavaScript, C, C++, Java, Kotlin, Swift, and more |
| 📊 Progress Tracking | Sessions, messages, and topics are persisted locally across runs |
| 📝 Transcript Saving | Export any session as a Markdown file for future reference |
| ⌨️ Shortcut Commands | `hint`, `explain`, `example`, `save` — all available mid-session |
| 🔄 Context Management | Conversation history is automatically trimmed to stay within token limits |
| 🎨 Rich Terminal UI | Colour-coded panels, tables, syntax-highlighted code, and live Markdown rendering |

---

## Supported Languages

| # | Language | Focus |
|---|---|---|
| 1 | 🐍 Python | Beginner-friendly |
| 2 | ⚙️ Rust | Systems programming |
| 3 | 🐹 Go | Cloud & backend |
| 4 | 📘 TypeScript | Typed JavaScript |
| 5 | 🟨 JavaScript | Web & Node.js |
| 6 | 🖥️ Bash | Shell scripting |
| 7 | 🗄️ SQL | Database queries |
| 8 | 🌙 Lua | Scripting & games |
| 9 | 💙 PowerShell | Windows automation |
| 10 | 🔵 C | Low-level systems |
| 11 | 🔷 C++ | Performance & systems |
| 12 | ☕ Java | Enterprise & Android |
| 13 | 🟣 Kotlin | Modern JVM / Android |
| 14 | 🍎 Swift | iOS & macOS |
| 15 | 💎 Ruby | Web & scripting |
| 16 | 🐘 PHP | Web backend |
| 17 | 🔴 Scala | Functional & big data |
| 18 | λ Haskell | Pure functional |
| 19 | ⚡ Zig | Modern systems |
| 0 | ✨ Other | You choose! |

---

## Learning Modes

### 📚 Lesson
A structured, step-by-step lesson on any topic you choose. The tutor explains the concept from first principles, provides commented code examples, and ends with a small exercise for you to try.

**Best for:** Learning something new, filling knowledge gaps.

---

### 🧠 Quiz
The tutor asks you 3–5 questions one at a time, waits for your answer, then gives feedback and a brief explanation before moving to the next question.

**Best for:** Testing and reinforcing what you already know.

---

### 💡 Code Challenge
You receive a coding problem with a clear description, example input/output, and a starter template. The tutor does **not** give you the solution — it guides you toward it.

**Best for:** Practising problem-solving and building muscle memory.

---

### 🔍 Code Review
Paste any code snippet and receive detailed feedback: correctness, style, performance, security, and idiomatic improvements.

**Best for:** Improving existing code, learning best practices.

---

### 🐛 Debug Helper *(new in v2)*
Paste broken code and the tutor diagnoses the issue, explains what went wrong, and guides you to the fix without just handing you the answer.

**Best for:** Understanding bugs rather than just fixing them.

---

### 💬 Ask Anything
Free-form conversation with the tutor. Ask any question about the language, ecosystem, tooling, or concepts.

**Best for:** Quick questions, exploring ideas, general discussion.

---

### 🗺️ Learning Path
Receive a personalised roadmap organised into Beginner → Intermediate → Advanced phases, with key topics, mini-project ideas, and free resource recommendations.

**Best for:** Starting a new language, planning your study schedule.

---

### 📝 Cheat Sheet *(new in v2)*
Get a concise, well-organised quick-reference for any topic — syntax tables, common patterns, and code snippets in one place.

**Best for:** Quick reference while coding, revision before interviews.

---

## Requirements

- **Python** 3.10 or higher
- **Anthropic API key** — get one free at [console.anthropic.com](https://console.anthropic.com)
- Internet connection

### Python packages

```
anthropic>=0.25.0
rich>=13.0.0
```

---

## Installation

### 1. Clone or download

```bash
git clone https://github.com/yourname/CLI2CODE.git
cd CLI2CODE
```

Or simply download `CLI2CODE.py` directly.

### 2. Install dependencies

```bash
pip install anthropic rich
```

Using a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows CMD
.venv\Scripts\Activate.ps1       # PowerShell

pip install anthropic rich
```

### 3. Set your API key

**Linux / macOS (bash/zsh):**
```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

Add to `~/.bashrc` or `~/.zshrc` to make it permanent.

**Windows CMD:**
```cmd
set ANTHROPIC_API_KEY=sk-ant-...
```

**Windows PowerShell:**
```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-..."
```

---

## Configuration

| Environment Variable | Default | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | *(required)* | Your Anthropic API key |
| `CLI_TEACHER_MODEL` | `claude-sonnet-4-20250514` | Override the Claude model |

### Changing the model

```bash
# Use a faster / cheaper model
export CLI_TEACHER_MODEL=claude-haiku-4-20250514

# Use the most capable model
export CLI_TEACHER_MODEL=claude-opus-4-20250514
```

---

## Usage

```bash
python CLI2CODE.py
```

### Typical flow

```
1. App starts → shows your progress summary (if any)
2. Pick a language  (e.g. Python)
3. Pick your experience level  (e.g. intermediate)
4. Pick a mode  (e.g. Code Challenge)
5. Optionally enter a topic  (e.g. "binary search")
6. Chat with the tutor — ask questions, submit answers, paste code
7. Type quit to end the session
8. Optionally save a transcript
9. Choose to start another session or exit
```

---

## In-Session Commands

These commands can be typed at any `You:` prompt during a session:

| Command | Alias | Action |
|---|---|---|
| `quit` / `exit` | `q` | End the session and save progress |
| `new` / `restart` | `n` | Save progress and start a new session immediately |
| `save` | `s` | Save the full session transcript as a Markdown file |
| `hint` | `h` | Ask the tutor for a hint (without revealing the answer) |
| `explain` | `e` | Re-explain the last concept in a different way |
| `example` | `ex` | Show another code example for the current concept |
| `help` / `?` | | Display the command reference table |

---

## Progress Tracking

Progress is automatically saved to `~/.cli_teacher_progress.json` after every session.

### What is tracked

- **Per session:** date, language, mode, topics discussed, message count
- **Per language:** total sessions, total messages, list of topics covered
- **Global:** total message count across all sessions

### Viewing your progress

Progress is displayed as a table every time you launch the app:

```
📊 Your Progress
 Language    Sessions   Messages   Topics Covered
 ──────────────────────────────────────────────────
 Python          4         38      loops, functions, classes, decorators +2 more
 Rust            2         21      ownership, borrowing, lifetimes
```

### Resetting progress

```bash
rm ~/.cli_teacher_progress.json
```

---

## Session Transcripts

At the end of each session you are asked if you want to save a transcript. You can also type `save` at any point during a session.

Transcripts are saved as Markdown files in `~/.cli_teacher_notes/`:

```
~/.cli_teacher_notes/
  python_lesson_20260509_143022.md
  rust_challenge_20260510_091145.md
```

Each file contains the full conversation formatted as:

```markdown
# CLI Teacher — Python / lesson
_Saved: May 09, 2026 14:30_

---

**You:** Please teach me a structured lesson on **decorators** in Python...

**CodeTeach:** ## Python Decorators
...
```

---

## Project Structure

```
cli-teacher/
├── CLI2CODE.py          # Main application (single-file)
├── README.md            # This file
└── requirements.txt     # Optional — for pip install -r
```

### Runtime files (created automatically)

```
~/.cli_teacher_progress.json    # Progress database
~/.cli_teacher_notes/           # Saved session transcripts
```

---

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│                      CLI Teacher                        │
│                                                         │
│  User Input  ──►  Message History  ──►  Anthropic API  │
│                        │                      │         │
│              trim_history()           Claude streams    │
│              (keeps ≤40 msgs)         tokens back       │
│                        │                      │         │
│              Progress saved  ◄──  stream_response()    │
│              to JSON file             renders Markdown  │
└─────────────────────────────────────────────────────────┘
```

### Key components

| Function / Component | Purpose |
|---|---|
| `main()` | Entry point — orchestrates the outer session loop |
| `run_session()` | Inner conversation loop for a single session |
| `stream_response()` | Streams Claude's reply and renders it live |
| `initial_prompt()` | Builds the mode-specific opening message |
| `handle_shortcut()` | Processes `hint`, `explain`, `example` commands |
| `trim_history()` | Keeps message history within the context window |
| `record_session()` | Persists session data to the progress file |
| `save_note()` | Exports a session transcript as Markdown |
| `build_system()` | Constructs the system prompt with language/level context |
| `collect_pasted_code()` | Reads multi-line code paste terminated by `END` |

### System prompt design

The tutor persona (`CodeTeach`) is defined in `SYSTEM_PROMPT` and injected as the `system` parameter on every API call. It instructs Claude to:

- Adapt explanations to the student's experience level
- Always include commented, runnable code examples
- Ask follow-up questions to check understanding
- Use Markdown formatting consistently
- Present quiz questions one at a time

---

## Improvements Over v1

| Area | v1 | v2 (this version) |
|---|---|---|
| Languages | 10 | 19 + custom |
| Modes | 6 | 8 (added Debug Helper, Cheat Sheet) |
| Max tokens | 2 048 | 4 096 |
| Context management | None | `trim_history()` — keeps ≤ 40 messages |
| Error handling | None | `APIStatusError`, `APIConnectionError` caught |
| Shortcut commands | None | `hint`, `explain`, `example`, `save`, `help` |
| Transcript saving | None | Auto-save to `~/.cli_teacher_notes/` |
| Progress stats | Sessions + topics | Sessions + topics + message counts |
| Model override | Hardcoded | `CLI_TEACHER_MODEL` env var |
| Code paste modes | review only | review + debug |
| Topic tracking | Simple word split | Regex word extraction with dedup + cap |
| PowerShell setup | Missing | Added `$env:` instructions |
| Type hints | Partial | Full (`Optional`, `list[dict]`, etc.) |

---

## Troubleshooting

### `ANTHROPIC_API_KEY not set`
Set the environment variable as shown in [Installation](#installation). Make sure there are no extra spaces or quotes around the key value.

### `Missing dependency: run pip install anthropic rich`
Run:
```bash
pip install anthropic rich
```
If you have multiple Python versions, use `pip3` or `python -m pip`.

### Responses cut off mid-sentence
The model hit the `MAX_TOKENS` limit. This is set to 4 096 by default. For very long roadmaps or cheat sheets you can increase it by editing `MAX_TOKENS` at the top of `CLI2CODE.py`.

### Old conversation context is lost
The app keeps the last 40 messages in context (`MAX_HISTORY`). For very long sessions, early messages are trimmed. The first two messages (opening exchange) are always preserved as an anchor.

### API rate limit errors
Anthropic free-tier accounts have rate limits. Wait a moment and try again, or upgrade your plan at [console.anthropic.com](https://console.anthropic.com).

### Progress file corrupted
```bash
rm ~/.cli_teacher_progress.json
```
The app will create a fresh one on next launch.

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-improvement`
3. Make your changes in `CLI2CODE.py`
4. Test manually with a few sessions
5. Open a pull request with a clear description of what changed and why

### Ideas for contributions

- Add a `--language` / `--mode` CLI flag to skip the menus
- Export progress as a CSV or HTML report
- Add a `flashcard` mode for vocabulary/syntax drilling
- Support streaming to a file (for piping output)
- Add a config file (`~/.cli_teacher_config.json`) for persistent preferences

---

## License

MIT — free to use, modify, and distribute.

---

*Built with [Anthropic Claude](https://anthropic.com) and [Rich](https://github.com/Textualize/rich).*

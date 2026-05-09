#!/usr/bin/env python3
"""
CLI Teacher — An AI-powered programming language tutor.

Supports Python, Rust, Go, TypeScript, JavaScript, Bash, SQL, Lua,
PowerShell, C, C++, Java, Kotlin, Swift, Ruby, PHP, Scala, Haskell,
Zig, and more.

Usage:
    python CLI2CODE.py

Requirements:
    pip install anthropic rich

Environment:
    ANTHROPIC_API_KEY  — your Anthropic API key (required)
    CLI_TEACHER_MODEL  — override the default Claude model (optional)
"""

import os
import sys
import json
import time
import textwrap
import re
from pathlib import Path
from datetime import datetime
from typing import Optional

# ─── Dependency checks ────────────────────────────────────────────────────────

try:
    import anthropic
except ImportError:
    print("Missing dependency: run  pip install anthropic rich")
    sys.exit(1)

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt, Confirm
    from rich.syntax import Syntax
    from rich.markdown import Markdown
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich import box
    from rich.text import Text
    from rich.columns import Columns
    from rich.rule import Rule
    from rich.align import Align
except ImportError:
    print("Missing dependency: run  pip install anthropic rich")
    sys.exit(1)

# ─── Constants ────────────────────────────────────────────────────────────────

DEFAULT_MODEL   = "claude-sonnet-4-20250514"
MODEL           = os.environ.get("CLI_TEACHER_MODEL", DEFAULT_MODEL)
MAX_TOKENS      = 4096          # raised from 2048 for richer responses
MAX_HISTORY     = 40            # max messages kept in context window
PROGRESS_FILE   = Path.home() / ".cli_teacher_progress.json"
NOTES_DIR       = Path.home() / ".cli_teacher_notes"

LANGUAGES = {
    "1":  {"name": "Python",      "emoji": "🐍", "level": "Beginner-friendly"},
    "2":  {"name": "Rust",        "emoji": "⚙️",  "level": "Systems programming"},
    "3":  {"name": "Go",          "emoji": "🐹", "level": "Cloud & backend"},
    "4":  {"name": "TypeScript",  "emoji": "📘", "level": "Typed JavaScript"},
    "5":  {"name": "JavaScript",  "emoji": "🟨", "level": "Web & Node.js"},
    "6":  {"name": "Bash",        "emoji": "🖥️",  "level": "Shell scripting"},
    "7":  {"name": "SQL",         "emoji": "🗄️",  "level": "Database queries"},
    "8":  {"name": "Lua",         "emoji": "🌙", "level": "Scripting & games"},
    "9":  {"name": "PowerShell",  "emoji": "💙", "level": "Windows automation"},
    "10": {"name": "C",           "emoji": "🔵", "level": "Low-level systems"},
    "11": {"name": "C++",         "emoji": "🔷", "level": "Performance & systems"},
    "12": {"name": "Java",        "emoji": "☕", "level": "Enterprise & Android"},
    "13": {"name": "Kotlin",      "emoji": "🟣", "level": "Modern JVM / Android"},
    "14": {"name": "Swift",       "emoji": "🍎", "level": "iOS & macOS"},
    "15": {"name": "Ruby",        "emoji": "💎", "level": "Web & scripting"},
    "16": {"name": "PHP",         "emoji": "🐘", "level": "Web backend"},
    "17": {"name": "Scala",       "emoji": "🔴", "level": "Functional & big data"},
    "18": {"name": "Haskell",     "emoji": "λ",  "level": "Pure functional"},
    "19": {"name": "Zig",         "emoji": "⚡", "level": "Modern systems"},
    "0":  {"name": "Other",       "emoji": "✨", "level": "You choose!"},
}

MODES = {
    "1": {"name": "📚 Lesson",          "key": "lesson",    "desc": "Structured lesson on a topic"},
    "2": {"name": "🧠 Quiz",            "key": "quiz",      "desc": "Test your knowledge"},
    "3": {"name": "💡 Code Challenge",  "key": "challenge", "desc": "Solve a coding problem"},
    "4": {"name": "🔍 Code Review",     "key": "review",    "desc": "Paste code for AI feedback"},
    "5": {"name": "💬 Ask Anything",    "key": "chat",      "desc": "Free-form Q&A with the tutor"},
    "6": {"name": "🗺️  Learning Path",  "key": "path",      "desc": "Get a personalised roadmap"},
    "7": {"name": "🐛 Debug Helper",    "key": "debug",     "desc": "Paste broken code for diagnosis"},
    "8": {"name": "📝 Cheat Sheet",     "key": "cheatsheet","desc": "Quick-reference summary of a topic"},
}

EXPERIENCE_LEVELS = {
    "1": "complete beginner",
    "2": "some experience",
    "3": "intermediate",
    "4": "advanced",
}

SYSTEM_PROMPT = """\
You are CodeTeach — an expert, encouraging programming tutor with deep knowledge of {language}.

Your teaching style:
- Break concepts down clearly, from first principles
- Use concrete, runnable code examples with every explanation
- Add inline comments to ALL code snippets
- Ask the student a follow-up question to check understanding
- Be warm, patient, and motivating — celebrate progress
- If the student makes a mistake, guide them without just giving the answer
- Adapt your depth and vocabulary to the student's experience level

Formatting rules:
- Use Markdown headings (##, ###) to organise lessons
- Wrap ALL code in fenced code blocks with the language tag, e.g. ```{lang_lower}
- Use bullet lists and numbered steps where appropriate
- Keep each response focused — don't dump everything at once
- For quizzes, present ONE question at a time and wait for the answer

Current date: {date}
Student experience level: {level}
"""

console = Console()

# ─── Progress & notes ─────────────────────────────────────────────────────────

def load_progress() -> dict:
    """Load progress data from disk, returning a safe default on failure."""
    if PROGRESS_FILE.exists():
        try:
            return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"sessions": [], "languages": {}, "total_messages": 0}


def save_progress(data: dict) -> None:
    """Persist progress data to disk."""
    try:
        PROGRESS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception as exc:
        console.print(f"[dim red]Warning: could not save progress — {exc}[/dim red]")


def record_session(
    progress: dict,
    language: str,
    mode: str,
    topics: list[str],
    message_count: int,
) -> None:
    """Append a session record and update per-language stats."""
    progress.setdefault("sessions", []).append({
        "date":     datetime.now().isoformat(),
        "language": language,
        "mode":     mode,
        "topics":   topics,
        "messages": message_count,
    })
    lang_stats = (
        progress
        .setdefault("languages", {})
        .setdefault(language, {"sessions": 0, "topics": [], "messages": 0})
    )
    lang_stats["sessions"]  += 1
    lang_stats["messages"]  += message_count
    for t in topics:
        if t and t not in lang_stats["topics"]:
            lang_stats["topics"].append(t)
    progress["total_messages"] = progress.get("total_messages", 0) + message_count
    save_progress(progress)


def save_note(language: str, mode: str, content: str) -> Path:
    """Save a session transcript as a Markdown note."""
    NOTES_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = NOTES_DIR / f"{language.lower()}_{mode}_{timestamp}.md"
    header = (
        f"# CLI Teacher — {language} / {mode}\n"
        f"_Saved: {datetime.now().strftime('%B %d, %Y %H:%M')}_\n\n---\n\n"
    )
    filename.write_text(header + content, encoding="utf-8")
    return filename

# ─── UI helpers ───────────────────────────────────────────────────────────────

def clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def banner() -> None:
    art = Text()
    art.append("  ╔══════════════════════════════════════════╗\n", style="bold cyan")
    art.append("  ║   ", style="bold cyan")
    art.append("🎓 CLI Teacher", style="bold white")
    art.append("  —  AI Programming Tutor   ", style="bold yellow")
    art.append("║\n", style="bold cyan")
    art.append("  ║   ", style="bold cyan")
    art.append(f"  Model: {MODEL:<36}", style="dim")
    art.append("║\n", style="bold cyan")
    art.append("  ╚══════════════════════════════════════════╝\n", style="bold cyan")
    console.print(art)


def show_progress_summary(progress: dict) -> None:
    """Render a compact progress table if any sessions exist."""
    langs = progress.get("languages", {})
    if not langs:
        return

    table = Table(
        title="📊 Your Progress",
        box=box.SIMPLE_HEAVY,
        style="dim",
        show_lines=False,
    )
    table.add_column("Language",       style="bold cyan")
    table.add_column("Sessions",       justify="center", style="green")
    table.add_column("Messages",       justify="center", style="yellow")
    table.add_column("Topics Covered", style="white")

    for lang, stats in langs.items():
        topics      = stats.get("topics", [])
        topics_str  = ", ".join(topics[:5])
        if len(topics) > 5:
            topics_str += f" +{len(topics) - 5} more"
        table.add_row(
            lang,
            str(stats.get("sessions", 0)),
            str(stats.get("messages", 0)),
            topics_str or "—",
        )

    console.print(table)
    console.print()


def pick_language() -> tuple[str, str]:
    """Render language menu and return (name, emoji)."""
    console.print(Panel("[bold]Choose a language to learn[/bold]", style="cyan"))

    # Two-column layout for the language table
    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    table.add_column("Key",   style="bold yellow", width=5)
    table.add_column("Lang",  style="bold white",  width=14)
    table.add_column("Emoji", width=4)
    table.add_column("Focus", style="dim",         width=22)

    for key, info in LANGUAGES.items():
        table.add_row(f"[{key}]", info["name"], info["emoji"], info["level"])

    console.print(table)

    valid_keys = list(LANGUAGES.keys())
    choice = Prompt.ask("\nEnter number", choices=valid_keys, default="1")
    lang   = LANGUAGES[choice]

    if choice == "0":
        name = Prompt.ask("  Which language?").strip() or "Unknown"
        return name, "✨"

    return lang["name"], lang["emoji"]


def pick_mode() -> tuple[str, str]:
    """Render mode menu and return (mode_key, mode_name)."""
    console.print(Panel("[bold]What would you like to do?[/bold]", style="cyan"))

    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    table.add_column("Key",  style="bold yellow", width=4)
    table.add_column("Mode", style="bold white",  width=24)
    table.add_column("Description", style="dim")

    for key, info in MODES.items():
        table.add_row(f"[{key}]", info["name"], info["desc"])

    console.print(table)

    choice = Prompt.ask("\nEnter number", choices=list(MODES.keys()), default="1")
    m = MODES[choice]
    return m["key"], m["name"]


def pick_level() -> str:
    """Return a human-readable experience level string."""
    console.print("\n[bold]Your experience level with this language?[/bold]")
    for k, v in EXPERIENCE_LEVELS.items():
        console.print(f"  [{k}] {v}")
    choice = Prompt.ask("Level", choices=list(EXPERIENCE_LEVELS.keys()), default="1")
    return EXPERIENCE_LEVELS[choice]


def show_help() -> None:
    """Print in-session command reference."""
    table = Table(title="In-Session Commands", box=box.SIMPLE, style="dim")
    table.add_column("Command",     style="bold yellow")
    table.add_column("Action",      style="white")
    table.add_column("Alias",       style="dim")

    rows = [
        ("quit / exit",  "End session and save progress",   "q"),
        ("new / restart","Start a new session immediately",  "n"),
        ("save",         "Save transcript as Markdown note", "s"),
        ("hint",         "Ask the tutor for a hint",         "h"),
        ("explain",      "Re-explain the last concept",      "e"),
        ("example",      "Show another code example",        "ex"),
        ("help",         "Show this command list",           "?"),
    ]
    for cmd, action, alias in rows:
        table.add_row(cmd, action, alias)

    console.print(table)

# ─── AI interaction ───────────────────────────────────────────────────────────

def build_system(language: str, level: str) -> str:
    return SYSTEM_PROMPT.format(
        language=language,
        lang_lower=language.lower(),
        level=level,
        date=datetime.now().strftime("%B %d, %Y"),
    )


def trim_history(messages: list[dict]) -> list[dict]:
    """
    Keep the conversation within MAX_HISTORY messages.
    Always preserves the first user message (context anchor) and
    trims from the middle to avoid losing recent context.
    """
    if len(messages) <= MAX_HISTORY:
        return messages
    # Keep first 2 (opening exchange) + most recent (MAX_HISTORY - 2)
    return messages[:2] + messages[-(MAX_HISTORY - 2):]


def stream_response(
    client: anthropic.Anthropic,
    messages: list[dict],
    system: str,
) -> str:
    """
    Stream the assistant reply token-by-token, rendering Markdown live.
    Returns the full response text.
    """
    full_text = ""
    console.print()
    console.rule("[dim]CodeTeach[/dim]")
    console.print()

    try:
        with client.messages.stream(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=system,
            messages=trim_history(messages),
        ) as stream:
            buffer = ""
            for text in stream.text_stream:
                full_text += text
                buffer    += text
                # Flush complete lines for smooth rendering
                if "\n" in buffer:
                    lines = buffer.split("\n")
                    for line in lines[:-1]:
                        console.print(Markdown(line) if line.strip() else "")
                    buffer = lines[-1]
            if buffer:
                console.print(Markdown(buffer) if buffer.strip() else "")

    except anthropic.APIStatusError as exc:
        console.print(f"\n[bold red]API error {exc.status_code}:[/bold red] {exc.message}")
        return "[error]"
    except anthropic.APIConnectionError:
        console.print("\n[bold red]Connection error — check your internet connection.[/bold red]")
        return "[error]"
    except KeyboardInterrupt:
        console.print("\n[dim]Response interrupted.[/dim]")

    console.print()
    return full_text


def initial_prompt(mode: str, language: str, topic: Optional[str], level: str) -> str:
    """Build the opening user message for each mode."""
    difficulty_map = {
        "complete beginner": "easy",
        "some experience":   "easy-medium",
        "intermediate":      "medium",
        "advanced":          "hard",
    }

    if mode == "lesson":
        subject = topic or f"the basics of {language}"
        return (
            f"Please teach me a structured lesson on **{subject}** in {language}. "
            f"I am a {level}. Start with the core concept, show runnable code examples "
            "with comments, explain what each part does, then give me a small exercise to try."
        )

    elif mode == "quiz":
        subject = topic or language
        return (
            f"Give me a quiz about **{subject}** in {language} for a {level}. "
            "Ask me 3–5 questions ONE AT A TIME — wait for my answer before moving on. "
            "After each answer, tell me if I'm right and briefly explain why. "
            "Start with question 1 now."
        )

    elif mode == "challenge":
        difficulty = difficulty_map.get(level, "medium")
        subject    = f" related to {topic}" if topic else ""
        return (
            f"Give me a {difficulty} coding challenge in {language}{subject}. "
            "Describe the problem clearly, state the expected input/output with examples, "
            "and include a starter template with TODO comments. Do NOT give the solution yet."
        )

    elif mode == "review":
        return (
            "I have some code I'd like you to review. "
            "Please wait — I'll paste it in my next message."
        )

    elif mode == "debug":
        return (
            "I have some broken code I need help debugging. "
            "Please wait — I'll paste it in my next message."
        )

    elif mode == "path":
        return (
            f"Create a personalised learning roadmap for **{language}** for a {level}. "
            "Organise it in phases (Beginner → Intermediate → Advanced), "
            "list key topics per phase with estimated time, "
            "suggest 2–3 mini-projects per phase, "
            "and recommend free resources (docs, tutorials, books)."
        )

    elif mode == "cheatsheet":
        subject = topic or language
        return (
            f"Create a concise, well-organised cheat sheet for **{subject}** in {language}. "
            "Cover the most important syntax, built-in functions/methods, and common patterns. "
            "Use tables and code blocks. Make it something I can reference quickly."
        )

    else:  # chat
        subject = topic or language
        return f"Hi! I want to learn more about **{subject}** in {language}. I'm a {level}. Let's chat!"


def handle_shortcut(cmd: str, messages: list[dict], client: anthropic.Anthropic, system: str) -> Optional[str]:
    """
    Handle single-word shortcut commands inside a session.
    Returns the assistant reply if a shortcut was triggered, else None.
    """
    shortcuts = {
        "hint":    "Give me a hint for the current problem without revealing the full answer.",
        "explain": "Please re-explain the last concept you covered in a different way, with a fresh example.",
        "example": "Show me another code example illustrating the same concept.",
        "h":       "Give me a hint for the current problem without revealing the full answer.",
        "e":       "Please re-explain the last concept you covered in a different way, with a fresh example.",
        "ex":      "Show me another code example illustrating the same concept.",
    }
    if cmd in shortcuts:
        msg = shortcuts[cmd]
        messages.append({"role": "user", "content": msg})
        reply = stream_response(client, messages, system)
        messages.append({"role": "assistant", "content": reply})
        return reply
    return None


def collect_pasted_code(prompt_text: str) -> str:
    """Prompt the user to paste a multi-line code block terminated by END."""
    console.print(f"[dim]{prompt_text}[/dim]")
    console.print("[dim](Type or paste your code, then type END on a new line)[/dim]\n")
    lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == "END":
                break
            lines.append(line)
        except EOFError:
            break
    return "\n".join(lines)

# ─── Session loop ─────────────────────────────────────────────────────────────

def run_session(
    client:     anthropic.Anthropic,
    language:   str,
    lang_emoji: str,
    mode:       str,
    mode_name:  str,
    level:      str,
    progress:   dict,
) -> None:
    clear()
    banner()
    console.print(Panel(
        f"{lang_emoji} [bold]{language}[/bold]  ·  {mode_name}  ·  level: [italic]{level}[/italic]",
        style="green",
    ))
    console.print("[dim]Type [bold]help[/bold] or [bold]?[/bold] to see available commands.[/dim]\n")

    # Optional topic prompt (not needed for review/debug/path/cheatsheet)
    topic: Optional[str] = None
    if mode in ("lesson", "quiz", "challenge", "chat"):
        topic = Prompt.ask(
            f"[yellow]Topic or concept to focus on[/yellow] (or press Enter for a suggestion)",
            default="",
        ).strip() or None

    system   = build_system(language, level)
    messages: list[dict] = []
    transcript_parts: list[str] = []

    # ── Opening exchange ──────────────────────────────────────────────────────
    opening = initial_prompt(mode, language, topic, level)
    messages.append({"role": "user", "content": opening})
    transcript_parts.append(f"**You:** {opening}\n")

    reply = stream_response(client, messages, system)
    if reply != "[error]":
        messages.append({"role": "assistant", "content": reply})
        transcript_parts.append(f"**CodeTeach:** {reply}\n")

    topics_covered: list[str] = [topic] if topic else []
    code_paste_pending = mode in ("review", "debug")

    console.rule("[dim]Type your response — 'help' for commands[/dim]")

    # ── Conversation loop ─────────────────────────────────────────────────────
    while True:
        try:
            user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not user_input:
            continue

        cmd = user_input.lower()

        # ── Exit commands ─────────────────────────────────────────────────────
        if cmd in ("quit", "exit", "q"):
            break

        if cmd in ("new", "restart", "n"):
            record_session(progress, language, mode, topics_covered, len(messages))
            return

        # ── Help ──────────────────────────────────────────────────────────────
        if cmd in ("help", "?"):
            show_help()
            continue

        # ── Save transcript ───────────────────────────────────────────────────
        if cmd in ("save", "s"):
            path = save_note(language, mode, "\n\n".join(transcript_parts))
            console.print(f"[green]✅ Transcript saved to:[/green] {path}")
            continue

        # ── Shortcut commands (hint / explain / example) ──────────────────────
        shortcut_reply = handle_shortcut(cmd, messages, client, system)
        if shortcut_reply is not None:
            if shortcut_reply != "[error]":
                transcript_parts.append(f"**CodeTeach:** {shortcut_reply}\n")
            console.rule("[dim]Continue the conversation[/dim]")
            continue

        # ── Code paste for review / debug modes ───────────────────────────────
        if code_paste_pending:
            code_paste_pending = False
            code_block = collect_pasted_code(
                "Paste your code below."
                if mode == "review"
                else "Paste the broken code below."
            )
            action = "review" if mode == "review" else "debug and fix"
            user_input = (
                f"Here is my code:\n```\n{code_block}\n```\n"
                f"Please {action} it."
            )

        # ── Normal message ────────────────────────────────────────────────────
        messages.append({"role": "user", "content": user_input})
        transcript_parts.append(f"**You:** {user_input}\n")

        reply = stream_response(client, messages, system)
        if reply != "[error]":
            messages.append({"role": "assistant", "content": reply})
            transcript_parts.append(f"**CodeTeach:** {reply}\n")

        # Track meaningful topic words from user input
        for word in re.findall(r"\b[A-Za-z]{4,}\b", user_input):
            if word.lower() not in (t.lower() for t in topics_covered):
                topics_covered.append(word)
                if len(topics_covered) > 30:   # cap to avoid bloat
                    topics_covered = topics_covered[-30:]

        console.rule("[dim]Continue the conversation — 'quit' to exit[/dim]")

    # ── End of session ────────────────────────────────────────────────────────
    record_session(progress, language, mode, topics_covered, len(messages))
    console.print("\n[bold green]✅ Session saved. Great work![/bold green]\n")

    if Confirm.ask("Save a transcript of this session?", default=False):
        path = save_note(language, mode, "\n\n".join(transcript_parts))
        console.print(f"[green]Transcript saved to:[/green] {path}\n")

# ─── API key check ────────────────────────────────────────────────────────────

def check_api_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if key:
        return key
    console.print(Panel(
        "[bold red]ANTHROPIC_API_KEY not set![/bold red]\n\n"
        "Get your key at [link=https://console.anthropic.com]console.anthropic.com[/link]\n\n"
        "Then run:\n"
        "  [bold]export ANTHROPIC_API_KEY=sk-ant-...[/bold]   (Linux/macOS)\n"
        "  [bold]set    ANTHROPIC_API_KEY=sk-ant-...[/bold]   (Windows CMD)\n"
        "  [bold]$env:ANTHROPIC_API_KEY='sk-ant-...'[/bold]   (PowerShell)\n",
        title="Setup Required",
        style="red",
    ))
    sys.exit(1)

# ─── Entry point ──────────────────────────────────────────────────────────────

def main() -> None:
    clear()
    banner()

    api_key = check_api_key()
    client  = anthropic.Anthropic(api_key=api_key)
    progress = load_progress()

    show_progress_summary(progress)

    console.print("[bold]Welcome to [cyan]CLI Teacher[/cyan] — your AI programming tutor![/bold]")
    console.print(
        "Type [yellow]quit[/yellow] at any prompt to exit  ·  "
        "[yellow]help[/yellow] inside a session for commands.\n"
    )

    while True:
        language, lang_emoji = pick_language()
        console.print()
        level = pick_level()
        console.print()
        mode, mode_name = pick_mode()

        run_session(client, language, lang_emoji, mode, mode_name, level, progress)

        console.print()
        if not Confirm.ask("Start another session?", default=True):
            break

        clear()
        banner()
        show_progress_summary(progress)

    # ── Farewell screen ───────────────────────────────────────────────────────
    clear()
    banner()
    show_progress_summary(progress)
    console.print(Panel(
        "[bold green]Thanks for learning with CLI Teacher! 🎉[/bold green]\n\n"
        f"Total sessions : [cyan]{len(progress.get('sessions', []))}[/cyan]\n"
        f"Total messages : [cyan]{progress.get('total_messages', 0)}[/cyan]\n"
        f"Languages      : [cyan]{', '.join(progress.get('languages', {}).keys()) or 'none yet'}[/cyan]\n\n"
        f"Notes saved to : [dim]{NOTES_DIR}[/dim]",
        style="green",
    ))


if __name__ == "__main__":
    main()

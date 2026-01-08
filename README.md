# append-only-journal

A command-line journal tool that stores entries in JSONL format.

## Two Versions

| File | Description | Best For |
|------|-------------|----------|
| `journal-lite.py` | Minimal version (~70 lines) | Learning basics, simple use |
| `journal.py` | Full-featured version (~300 lines) | Daily use, learning advanced concepts |

## Quick Start

```bash
# Add an entry
python journal.py add "Started learning Python today"

# View all entries
python journal.py replay

# Search entries
python journal.py search "python"
```

## Features Comparison

| Feature | journal-lite.py | journal.py |
|---------|:---------------:|:----------:|
| Add entries | ✓ | ✓ |
| Replay entries | ✓ | ✓ |
| Tags | — | ✓ |
| Search | — | ✓ |
| Statistics | — | ✓ |
| Date filtering | — | ✓ |
| Export to Markdown | — | ✓ |

## Usage

### journal-lite.py (Basic)

```bash
# Add entry
python journal-lite.py add "Your journal entry here"

# View all entries
python journal-lite.py replay

# Use custom log file
python journal-lite.py --log myjournal.jsonl add "Entry"
```

### journal.py (Enhanced)

```bash
# Add entry with tags
python journal.py add "Fixed login bug" --tags work,coding

# View entries with tag filter
python journal.py replay --tag work

# View entries since a date
python journal.py replay --since 2024-01-01

# Search entries
python journal.py search "bug"
python journal.py search "BUG" --case-sensitive

# Show statistics
python journal.py count

# Export to markdown
python journal.py export > journal.md
```

## Data Format

Entries are stored in JSONL (one JSON object per line):

```json
{"timestamp": "2024-01-08T10:30:00+00:00", "entry": "Basic entry"}
{"timestamp": "2024-01-08T14:00:00+00:00", "entry": "Tagged entry", "tags": ["work", "python"]}
```

**Why JSONL?**
- Each line is independent (corruption doesn't destroy everything)
- Append-only (just add to end of file)
- Human-readable
- Easy to process with other tools

## Learning Path

If you're learning Python, study the files in this order:

1. **journal-lite.py** — Core concepts:
   - Argument parsing with `argparse`
   - File I/O with `pathlib` and context managers (`with`)
   - JSON serialization
   - Function organization

2. **journal.py** — Advanced concepts:
   - Generators (`yield`)
   - Type hints (`Optional`, `Generator`)
   - Date parsing and comparison
   - Dictionary aggregation
   - String methods for search

## Requirements

- Python 3.9+
- No external dependencies (standard library only)

## License

MIT

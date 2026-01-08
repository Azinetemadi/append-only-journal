#!/usr/bin/env python3
"""
Enhanced CLI Journal - Learning Version

This version adds several features to help you learn:
- search: Find entries containing keywords
- count: Show statistics about your journal  
- export: Convert to markdown format
- tags: Organize entries with tags
- date filtering: View entries from specific time periods

Each addition demonstrates different Python concepts.
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Generator, Optional


DEFAULT_LOG = "journal.jsonl"


# =============================================================================
# CORE DATA FUNCTIONS
# =============================================================================

def iso_timestamp() -> str:
    """Generate ISO 8601 timestamp with local timezone."""
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def parse_timestamp(ts_string: str) -> Optional[datetime]:
    """
    Parse an ISO timestamp string back into a datetime object.
    
    NEW CONCEPT: Optional[datetime] means "returns datetime OR None"
    This is a type hint that helps catch bugs.
    """
    try:
        return datetime.fromisoformat(ts_string)
    except ValueError:
        return None


def load_entries(log_path: Path) -> Generator[dict, None, None]:
    """
    Load all entries from the journal file.
    
    NEW CONCEPT: Generator
    Instead of loading ALL entries into memory at once (list),
    a generator yields them one at a time. This handles huge files
    without running out of memory.
    
    The type hint Generator[dict, None, None] means:
    - Yields: dict
    - Accepts via .send(): None (we don't use this)
    - Returns on completion: None
    """
    if not log_path.exists():
        return  # Empty generator - yields nothing
    
    with log_path.open("r", encoding="utf-8") as handle:
        for line_num, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                # Log to stderr but keep going
                print(f"Warning: Invalid JSON on line {line_num}", file=sys.stderr)


# =============================================================================
# COMMAND HANDLERS
# =============================================================================

def cmd_add(log_path: Path, text: str, tags: Optional[list[str]] = None) -> int:
    """
    Append a new entry to the journal.
    
    IMPROVED: Now supports optional tags for organization.
    """
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    payload = {
        "timestamp": iso_timestamp(),
        "entry": text,
    }
    
    # Only add tags key if tags were provided
    if tags:
        payload["tags"] = tags
    
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + "\n")
    
    print(f"✓ Entry added to {log_path}")
    if tags:
        print(f"  Tags: {', '.join(tags)}")
    
    return 0


def cmd_replay(
    log_path: Path,
    since: Optional[str] = None,
    tag_filter: Optional[str] = None
) -> int:
    """
    Display journal entries with optional filtering.
    
    IMPROVED: 
    - Filter by date with --since
    - Filter by tag with --tag
    """
    if not log_path.exists():
        print(f"No journal found at {log_path}", file=sys.stderr)
        return 1
    
    # Parse the --since date if provided
    since_date = None
    if since:
        since_date = parse_timestamp(since + "T00:00:00+00:00")
        if not since_date:
            # Try parsing as full ISO timestamp
            since_date = parse_timestamp(since)
        if not since_date:
            print(f"Invalid date format: {since}", file=sys.stderr)
            return 1
    
    entries_shown = 0
    
    for entry in load_entries(log_path):
        # Apply date filter
        if since_date:
            entry_date = parse_timestamp(entry.get("timestamp", ""))
            if entry_date and entry_date < since_date:
                continue
        
        # Apply tag filter
        if tag_filter:
            entry_tags = entry.get("tags", [])
            if tag_filter.lower() not in [t.lower() for t in entry_tags]:
                continue
        
        # Display the entry
        timestamp = entry.get("timestamp", "unknown")
        text = entry.get("entry", "")
        tags = entry.get("tags", [])
        
        print(f"{timestamp} | {text}")
        if tags:
            print(f"  └─ tags: {', '.join(tags)}")
        
        entries_shown += 1
    
    if entries_shown == 0:
        print("No entries match your filters.", file=sys.stderr)
    
    return 0


def cmd_search(log_path: Path, keyword: str, case_sensitive: bool = False) -> int:
    """
    Search entries for a keyword.
    
    NEW COMMAND: Demonstrates string searching and case handling.
    """
    if not log_path.exists():
        print(f"No journal found at {log_path}", file=sys.stderr)
        return 1
    
    matches = 0
    search_term = keyword if case_sensitive else keyword.lower()
    
    for entry in load_entries(log_path):
        text = entry.get("entry", "")
        compare_text = text if case_sensitive else text.lower()
        
        if search_term in compare_text:
            timestamp = entry.get("timestamp", "unknown")
            print(f"{timestamp} | {text}")
            matches += 1
    
    print(f"\n─── Found {matches} matching entries ───")
    return 0


def cmd_count(log_path: Path) -> int:
    """
    Show journal statistics.
    
    NEW COMMAND: Demonstrates aggregation over data.
    """
    if not log_path.exists():
        print(f"No journal found at {log_path}", file=sys.stderr)
        return 1
    
    total = 0
    tag_counts: dict[str, int] = {}  # NEW: Type hint for dict
    earliest: Optional[datetime] = None
    latest: Optional[datetime] = None
    
    for entry in load_entries(log_path):
        total += 1
        
        # Count tags
        for tag in entry.get("tags", []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Track date range
        ts = parse_timestamp(entry.get("timestamp", ""))
        if ts:
            if earliest is None or ts < earliest:
                earliest = ts
            if latest is None or ts > latest:
                latest = ts
    
    # Display statistics
    print(f"📊 Journal Statistics")
    print(f"   Total entries: {total}")
    
    if earliest and latest:
        print(f"   Date range: {earliest.date()} to {latest.date()}")
    
    if tag_counts:
        print(f"   Tags used:")
        # Sort by count descending
        for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
            print(f"      {tag}: {count}")
    
    return 0


def cmd_export(log_path: Path, format: str = "markdown") -> int:
    """
    Export journal to different formats.
    
    NEW COMMAND: Demonstrates format conversion.
    Currently supports: markdown
    """
    if not log_path.exists():
        print(f"No journal found at {log_path}", file=sys.stderr)
        return 1
    
    if format == "markdown":
        print("# Journal Export\n")
        
        current_date = None
        
        for entry in load_entries(log_path):
            ts = parse_timestamp(entry.get("timestamp", ""))
            text = entry.get("entry", "")
            tags = entry.get("tags", [])
            
            # Group by date with headers
            if ts:
                entry_date = ts.strftime("%Y-%m-%d")
                if entry_date != current_date:
                    current_date = entry_date
                    print(f"\n## {current_date}\n")
            
            # Format entry
            time_str = ts.strftime("%H:%M") if ts else "??:??"
            print(f"- **{time_str}** — {text}")
            if tags:
                print(f"  - *Tags: {', '.join(tags)}*")
        
        return 0
    
    print(f"Unknown format: {format}", file=sys.stderr)
    return 1


# =============================================================================
# ARGUMENT PARSER
# =============================================================================

def build_parser() -> argparse.ArgumentParser:
    """
    Build the command-line argument parser.
    
    IMPROVED: More commands, better organization.
    """
    parser = argparse.ArgumentParser(
        description="Append-only CLI journal with JSONL persistence.",
        # NEW: Custom formatter for better help text
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s add "Had a great day"
  %(prog)s add "Fixed bug" --tags work,coding
  %(prog)s replay --since 2024-01-01
  %(prog)s search "coffee"
  %(prog)s count
  %(prog)s export --format markdown > journal.md
        """
    )
    
    parser.add_argument(
        "--log", "-l",  # NEW: Short form -l
        default=DEFAULT_LOG,
        help=f"Path to journal file (default: {DEFAULT_LOG})",
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # --- ADD command ---
    add_p = subparsers.add_parser("add", help="Add a new journal entry")
    add_p.add_argument("text", help="The journal entry text")
    add_p.add_argument(
        "--tags", "-t",
        help="Comma-separated tags (e.g., work,important)",
    )
    
    # --- REPLAY command ---
    replay_p = subparsers.add_parser("replay", help="Display journal entries")
    replay_p.add_argument(
        "--since", "-s",
        help="Show entries from this date onward (YYYY-MM-DD)",
    )
    replay_p.add_argument(
        "--tag",
        help="Filter by tag",
    )
    
    # --- SEARCH command ---
    search_p = subparsers.add_parser("search", help="Search entries")
    search_p.add_argument("keyword", help="Text to search for")
    search_p.add_argument(
        "--case-sensitive", "-c",
        action="store_true",  # NEW: Boolean flag (no value needed)
        help="Make search case-sensitive",
    )
    
    # --- COUNT command ---
    subparsers.add_parser("count", help="Show journal statistics")
    
    # --- EXPORT command ---
    export_p = subparsers.add_parser("export", help="Export to other formats")
    export_p.add_argument(
        "--format", "-f",
        default="markdown",
        choices=["markdown"],  # NEW: Restrict to valid options
        help="Output format (default: markdown)",
    )
    
    return parser


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main() -> int:
    """Main entry point - parse args and dispatch to handlers."""
    parser = build_parser()
    args = parser.parse_args()
    log_path = Path(args.log)
    
    # NEW PATTERN: Dictionary dispatch instead of if/elif chain
    # This is cleaner when you have many commands
    
    if args.command == "add":
        tags = args.tags.split(",") if args.tags else None
        return cmd_add(log_path, args.text, tags)
    
    elif args.command == "replay":
        return cmd_replay(log_path, args.since, args.tag)
    
    elif args.command == "search":
        return cmd_search(log_path, args.keyword, args.case_sensitive)
    
    elif args.command == "count":
        return cmd_count(log_path)
    
    elif args.command == "export":
        return cmd_export(log_path, args.format)
    
    # Should never reach here due to required=True on subparsers
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

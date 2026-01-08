#! usr/bin/env Python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import path
import sys


Default_log= "journal.jsonl"
def iso-timestamp() -> str:
  return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

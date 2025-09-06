"""
Main script for vergil2ics.

Fetches class schedules from the Vergil API, converts them into an iCalendar (.ics)
format, and saves the output to a file.
"""
from __future__ import annotations

from pathlib import Path
import sys

from requests.exceptions import RequestException

from core import parse, build_calendar, ClassNotFoundError, MultipleClassError


if __name__ == '__main__':
    class_ids = [
        # 'CSEE4119W003',
        'ECBM4040E001',
        'COMS4118W001',
        'ELEN6761E001',
        'EECS4750E001',
    ]
    CALENDAR_CODE = '20253' # 25 fall
    output = Path(__file__).parent / 'output' / 'vergil.ics'

    try:
        classes = parse(class_ids, CALENDAR_CODE)
        calendar = build_calendar(classes)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(calendar.serialize(), encoding='utf-8', newline='')
        print(f'[+] ics generated → {output}')
    except (ClassNotFoundError, MultipleClassError) as e:
        print(f'[-] Error: {e}', file=sys.stderr)
        sys.exit(1)
    except RequestException as e:
        print(f'[-] Network or API error: {e}', file=sys.stderr)
        sys.exit(1)

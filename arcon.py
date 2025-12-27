#!/usr/bin/env python3
from src.app import run_cli, run_web
import sys

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--ui':
        run_web()
    else:
        run_cli()
import re
import sys
from typing import List

def filter_changeset(lines:List[str], pattern:str, filename:str) -> None:
    re_expr = re.compile(pattern)
    
    with open(filename, 'w') as file:
        for item in filter(re_expr.match, lines):
            file.write(f"{item}\n")

if __name__ == "__main__":
    lines = [file.strip() for file in sys.stdin.readlines()]
    filter_changeset(lines, r'dags/.*\.py', '.changeset.dags')
    filter_changeset(lines, r'dags/.*\.py', '.changeset.plugins')
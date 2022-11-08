import re
import sys
from typing import List


def parse_airflow_changes(lines:List[str]):
    expr = re.compile(r'dags/.*\.py|plugins/.*\.py')
    return list(filter(expr.match, lines))

if __name__ == "__main__":
    lines = [file.strip() for file in sys.stdin.readlines()]
    for change in parse_airflow_changes(lines):
        print(change)
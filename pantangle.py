# CODE TANGLED FROM 'pantangle.md'

from __future__ import annotations

import json
import subprocess
import sys
from typing import Any, Callable, Iterator

# CODE BLOCK DELIMITER

CodeBlockItem = dict[str, tuple[tuple[Any, str, Any], str]]

# CODE BLOCK DELIMITER

def read_source(file_name: str) -> str:
    proc = subprocess.run(
        ["pandoc", "-t", "json", "-s", str(file_name)],
        capture_output=True,
    )
    source = str(proc.stdout.decode("utf-8"))
    return source

# CODE BLOCK DELIMITER

def process_code_block(item: CodeBlockItem) -> str:
    value = item["c"]
    (_, classes, _), content = value
    return content

# CODE BLOCK DELIMITER

def interleave(iterator: Iterator[str], value: str) -> Iterator[str]:
    first = True
    for item in iterator:
        if first:
            first = False
        else:
            yield value

        yield item

# CODE BLOCK DELIMITER

def tangle(source: str) -> Iterator[str]:
    for item in json.loads(source)["blocks"]:
        if item["t"] != "CodeBlock":
            continue

        res = process_code_block(item)
        yield res

# CODE BLOCK DELIMITER

CODE_BLOCK_DELIMITER = "\n# CODE BLOCK DELIMITER\n"


def main(file_name: str, sink: Callable[[str], None] = print) -> None:
    source = read_source(file_name)
    tangled = tangle(source)
    lines = interleave(tangled, CODE_BLOCK_DELIMITER)

    sink(f"# CODE TANGLED FROM '{file_name}'\n")
    for line in lines:
        sink(line)

# CODE BLOCK DELIMITER

if __name__ == "__main__":
    file_name = sys.argv[1]
    main(file_name)

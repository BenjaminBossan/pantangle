# CODE TANGLED FROM 'pantangle.md'

import json
import subprocess
import sys
from typing import Any, Callable, Dict, Iterator, List, Tuple, Union, cast

# CODE BLOCK DELIMITER

CodeBlockItem = Dict[str, Tuple[Tuple[Any, str, Any], str]]
GenericItem = Union[
    int, str, CodeBlockItem, List["GenericItem"], Dict[str, List["GenericItem"]]
]

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

def is_jupyter_output_cell(items: List[GenericItem]) -> bool:
    if len(items) < 2:
        return False

    item0 = items[0]
    if not isinstance(item0, list):
        return False

    if len(item0) < 2:
        return False

    item1 = item0[1]
    if not isinstance(item1, list):
        return False

    if len(item1) < 1:
        return False

    return item1[0] == "output"

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

def _tangle(item: GenericItem) -> Iterator[str]:
    if isinstance(item, (int, str)):
        return

    if isinstance(item, list):
        for subitem in item:
            yield from _tangle(subitem)
    else:  # dict
        type_ = item.get("t")
        if not type_:
            return

        if type_ == "CodeBlock":  # type: ignore
            item = cast(CodeBlockItem, item)  # for mypy
            res = process_code_block(item)
            yield res
        else:
            item = cast(Dict[str, List[GenericItem]], item)  # for mypy
            content: List[GenericItem] = item.get("c", [])
            if is_jupyter_output_cell(content):
                return

            for subitem in content:
                yield from _tangle(subitem)


def tangle(source: str) -> Iterator[str]:
    for item in json.loads(source)["blocks"]:
        yield from _tangle(item)

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

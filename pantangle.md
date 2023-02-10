# Description of the `pantangle.py` script

Using literator programming to document the script. The actual `pantangle.py` script was bootstrapped from this very document.

## Imports

First the imports. Only use the standard library to make it possible to run the script on as many systems as possible.

```python
import json
import subprocess
import sys
from typing import Any, Callable, Dict, Iterator, List, Tuple, Union, cast
```

## Custom type

A type to represent the CodeBlock item or a generic item returned by pandoc

```python
CodeBlockItem = Dict[str, Tuple[Tuple[Any, str, Any], str]]
GenericItem = Union[
    int, str, CodeBlockItem, List["GenericItem"], Dict[str, List["GenericItem"]]
]
```

## Functions

### Reading the source file

Shelling out to pandoc and use the `-t json` option to get a format that's easy
to work with.

```python
def read_source(file_name: str) -> str:
    proc = subprocess.run(
        ["pandoc", "-t", "json", "-s", str(file_name)],
        capture_output=True,
    )
    source = str(proc.stdout.decode("utf-8"))
    return source
```

From the pandoc item, return the actual content of the code block. There is additional information, like the programming language annotation (`classes`), which is currently not being used. Information here could also be used to tangle to different output files, like org tangle.

```python
def process_code_block(item: CodeBlockItem) -> str:
    value = item["c"]
    (_, classes, _), content = value
    return content
```

For Jupyter notebooks, the outputs of expressions are returned as code blocks too, but we don't want them to be tangled. Therefore, it is checked if an item is a Jupyter output cell. This seems to be a more or less sane way of checking.

```python
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
```

Helper function to interleave the code blocks with a unique delimiter. This makes it easier to later map back the code blocks to the original document. There are possibly better ways that would allow to automate the "detangling" process.

```python
def interleave(iterator: Iterator[str], value: str) -> Iterator[str]:
    first = True
    for item in iterator:
        if first:
            first = False
        else:
            yield value

        yield item
```

The actual function that tangles the code blocks. For each block, a recursive function is called that inspects its type. If an int or str, nothing is done. If a list, call itself on each member of the list. If a dict, check if it's a code block. If it is, its content will be yielded for tangling. If it's not a code block dict, call this function recursively on its values.

It ignores all types that are not code blocks and only yields those.

```python
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
```

The main file that glues the different parts together: reading the source, tangling it, interleaving, and printing to stdout.

```python
CODE_BLOCK_DELIMITER = "\n# CODE BLOCK DELIMITER\n"


def main(file_name: str, sink: Callable[[str], None] = print) -> None:
    source = read_source(file_name)
    tangled = tangle(source)
    lines = interleave(tangled, CODE_BLOCK_DELIMITER)

    sink(f"# CODE TANGLED FROM '{file_name}'\n")
    for line in lines:
        sink(line)
```

Extremely simple argument parsing.

```python
if __name__ == "__main__":
    file_name = sys.argv[1]
    main(file_name)
```

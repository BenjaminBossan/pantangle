# Description of the `pantangle.py` script

Using literator programming to document the script. The actual `pantangle.py` script was bootstrapped from this very document.

## Imports

First the imports. Only use the standard library to make it possible to run the script on as many systems as possible.

```python
import json
import subprocess
import sys
from typing import Any, Callable, Dict, Iterator, Tuple
```

## Custom type

A type to represent the CodeBlock item returned by pandoc

```python
CodeBlockItem = Dict[str, Tuple[Tuple[Any, str, Any], str]]
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

The actual function that tangles the code blocks. It ignores all types that are not code blocks and only yields those.

```python
def tangle(source: str) -> Iterator[str]:
    for item in json.loads(source)["blocks"]:
        if item["t"] != "CodeBlock":
            continue

        res = process_code_block(item)
        yield res
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

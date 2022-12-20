# Tangle code blocks from your documents

## Usage

Say you have a markdown file with code blocks and want to extract only these code blocks from the document. Use the standalone `pantangle.py` script to achieve this:

```sh
# print to console
python pantangle.py MY-DOCUMENT
# write to file
python pantangle.py MY-DOCUMENT > MY-FILE
```

## Installation

The script should work _as is_, so just copy it from the repo, no need to install any Python packages.

However, it does require pandoc and Python, so you need to have them on your system. To install pandoc, follow [these instructions](https://pandoc.org/installing.html), for Python, look [here](https://www.python.org/downloads/).

## Limitations

This should work on any document type [supported by pandoc](https://pandoc.org/MANUAL.html#general-options), so markdown, reStructuredText, org, asciidoc, etc. should work. However, it's only tested on markdown and reStructuredText so far.

## Background

The idea to "tangle" code from documents is taken from [Emacs org mode](https://orgmode.org/manual/Extracting-Source-Code.html), which also has this feature (it's just much more powerful).

## Development

Changes to the [`pantangle.py`](https://github.com/BenjaminBossan/pantangle/blob/main/pantangle.md) script should _not_ be made inside this script directly, but inside of `pantangle.md`, which is treated as the source of truth. It is written using literate programming. The script is then created by calling itself on the modified markdown file.

So once `pantangle.md` has been changed, run:

```python
python pantangle.py pantangle.md > foo.py && mv foo.py pantangle.py
```

To additionally run the test, do:

```python
python pantangle.py pantangle.md > foo.py && mv foo.py pantangle.py && python tests.py
```

Optionally, run `mypy` on the resulting code:

```python
mypy --strict pantangle.py
```

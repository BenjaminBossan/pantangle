import subprocess
import textwrap
import tempfile
from pathlib import Path


inputs = [
    (
        "md",
        """
        # Test code using markdown

        Some text with `code` that should be ignored

        ```
        def foo():
          return 123
        ```

        ## It goes on

        More text

        ```python
        class Bar():
          def __init__(self):
            self.bar = 456
        ```

        That's it
        """,
    ),

    (
        "rst",
        """
        Test code using markdown
        ========================

        Some text with ``code`` that should be ignored

        ::

           def foo():
             return 123

        It goes on
        ----------

        More text

        .. code:: python

           class Bar():
             def __init__(self):
               self.bar = 456

        That’s it
        """,
    ),
]


def run_test(suffix, inp):
    inp = textwrap.dedent(inp).strip()
    tmpdir = Path(tempfile.mkdtemp())
    f_name = tmpdir / ("input." + suffix)

    expected = textwrap.dedent(
        f"""
        # CODE TANGLED FROM '{f_name}'

        def foo():
          return 123

        # CODE BLOCK DELIMITER

        class Bar():
          def __init__(self):
            self.bar = 456
        """
    ).lstrip()

    with open(f_name, "w") as f:
        f.write(inp)

    proc = subprocess.run(
        ["python", "pantangle.py", str(f_name)],
        capture_output=True,
    )
    result = str(proc.stdout.decode("utf-8"))
    assert result == expected


if __name__ == "__main__":
    for suffix, inp in inputs:
        run_test(suffix, inp)
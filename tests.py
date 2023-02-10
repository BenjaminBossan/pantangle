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

        A simple expression

        ```python
        1 + 1
        ```

        That's it
        """,
    ),

    (
        "rst",
        """
        Test code using rst
        ===================

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

        A simple expression

        .. code:: python

            1 + 1

        That’s it
        """,
    ),

    (
        "ipynb",
        r"""
        {
           "cells" : [
              {
                 "cell_type" : "markdown",
                 "id" : "5a8e15ce",
                 "metadata" : {},
                 "source" : [
                    "# Test code using markdown\n",
                    "\n",
                    "Some text with `code` that should be ignored"
                 ]
              },
              {
                 "cell_type" : "code",
                 "execution_count" : 1,
                 "id" : "49eed0e3",
                 "metadata" : {},
                 "outputs" : [],
                 "source" : [
                    "def foo():\n",
                    "  return 123"
                 ]
              },
              {
                 "cell_type" : "markdown",
                 "id" : "855975f0",
                 "metadata" : {},
                 "source" : [
                    "## It goes on\n",
                    "\n",
                    "More text"
                 ]
              },
              {
                 "cell_type" : "code",
                 "execution_count" : 2,
                 "id" : "5c290f41",
                 "metadata" : {},
                 "outputs" : [],
                 "source" : [
                    "class Bar():\n",
                    "  def __init__(self):\n",
                    "    self.bar = 456"
                 ]
              },
              {
                 "cell_type" : "markdown",
                 "id" : "3b968013",
                 "metadata" : {},
                 "source" : [
                    "A simple expression"
                 ]
              },
              {
                 "cell_type" : "code",
                 "execution_count" : 3,
                 "id" : "0407be07",
                 "metadata" : {},
                 "outputs" : [
                    {
                       "data" : {
                          "text/plain" : [
                             "2"
                          ]
                       },
                       "execution_count" : 3,
                       "metadata" : {},
                       "output_type" : "execute_result"
                    }
                 ],
                 "source" : [
                    "1 + 1"
                 ]
              },
              {
                 "cell_type" : "markdown",
                 "id" : "129df485",
                 "metadata" : {},
                 "source" : [
                    "That's it"
                 ]
              }
           ],
           "metadata" : {
              "kernelspec" : {
                 "display_name" : "Python 3 (ipykernel)",
                 "language" : "python",
                 "name" : "python3"
              },
              "language_info" : {
                 "codemirror_mode" : {
                    "name" : "ipython",
                    "version" : 3
                 },
                 "file_extension" : ".py",
                 "mimetype" : "text/x-python",
                 "name" : "python",
                 "nbconvert_exporter" : "python",
                 "pygments_lexer" : "ipython3",
                 "version" : "3.10.9"
              }
           },
           "nbformat" : 4,
           "nbformat_minor" : 5
        }
        """
    )
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

        # CODE BLOCK DELIMITER

        1 + 1
        """
    ).lstrip()

    with open(f_name, "w") as f:
        f.write(inp)

    from pantangle import main

    results = []
    main(f_name, sink=results.append)
    results.append("")
    result = "\n".join(results)

    assert result == expected


if __name__ == "__main__":
    for suffix, inp in inputs:
        run_test(suffix, inp)
    print(f"All {len(inputs)} tests ran successfully")

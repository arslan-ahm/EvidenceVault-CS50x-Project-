# Vendored dependency notice

`mega.py`, `crypto.py`, and `errors.py` in this directory are vendored,
unmodified, from [odwyersoftware/mega.py](https://github.com/odwyersoftware/mega.py)
(the `master` branch as of 2026-08-09), licensed under the Apache License,
Version 2.0. The full license text is available at
<https://www.apache.org/licenses/LICENSE-2.0>.

Copyright belongs to the original authors (richardARPANET / O'Dwyer Software
and contributors). No modifications were made to the vendored source files.

## Why vendored instead of installed from PyPI

The published `mega.py` PyPI package (and its `master` branch `requirements.txt`)
hard-pins `pathlib==1.0.1`, an abandoned pre-3.4 backport of the stdlib
`pathlib` module. That backport's source does `from collections import
Sequence`, which was removed from `collections` in Python 3.10 (moved to
`collections.abc`). Installing it shadows the real stdlib `pathlib` module
for the entire Python process, which crashes Vercel's Python 3.12+ runtime at
cold start - before any application code runs - since the runtime's own
bootstrap does `import pathlib` internally. See
[odwyersoftware/mega.py#81](https://github.com/odwyersoftware/mega.py/issues/81)
for another report of the same broken dependency.

Vendoring the ~1,300 lines of actual client code (which only ever uses
`pathlib.Path` from the stdlib) avoids pulling in that phantom dependency
entirely.

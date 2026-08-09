"""Vendored copy of odwyersoftware/mega.py (Apache-2.0) — see NOTICE.md.

Vendored instead of installed from PyPI because the published `mega.py`
package hard-pins `pathlib==1.0.1`, an abandoned Python-2-era backport whose
`from collections import Sequence` crashes on Python 3.10+. Once installed,
it shadows the stdlib `pathlib` module for the whole process and breaks every
serverless function at cold start on Vercel - before this file, or any other
app code, ever runs. This code is unmodified apart from removing that phantom
dependency; the actual source only ever used `pathlib.Path` from the stdlib.
"""

from .mega import Mega  # noqa

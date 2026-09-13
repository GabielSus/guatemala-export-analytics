# EA-200 Hotfix

Fixes the three issues found during the first catalog load:

1. The official Banguat PDF is a two-column table. Plain PyMuPDF text extraction can separate the code and description columns, so the old same-line regex parsed 0 rows. The new parser reconstructs rows from positioned PDF words and has a text fallback.
2. `TopTariffItem` gained a description in a way that broke existing positional construction in tests. New optional enrichment fields are appended to dataclasses, preserving backwards compatibility.
3. The PowerShell loader previously continued after failed Python commands. It now checks every external command exit code and stops immediately on failure.

It also switches from deprecated `import fitz` to `import pymupdf`.

Official catalog URL used by the loader:

https://www.banguat.gob.gt/estaeco/ceie/sac.pdf

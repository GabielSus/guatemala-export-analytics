# EA-200 Hotfix v2

The parser already worked: the previous error dump showed roughly 17,000
catalog records ready to be inserted.

The failure happened during the PostgreSQL UPSERT because all records were
sent in one gigantic INSERT statement. With about 17,000 rows and four bound
values per row, the statement exceeded the practical bind-parameter limit.

This hotfix:

- loads the catalog in batches of 2,000 rows;
- commits every batch;
- keeps the load idempotent with `ON CONFLICT DO UPDATE`;
- ignores standalone 3-digit PDF page numbers such as `198`;
- does not touch the existing 313,104 export observations;
- can safely be rerun after the previous failed load.

Run:

```powershell
.\scripts\load_catalog.ps1
```

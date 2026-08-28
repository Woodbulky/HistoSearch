# data/

| Directory | Contents | Committed? |
|---|---|---|
| `raw/` | Downloaded source files, byte-for-byte as retrieved. **Immutable.** | no |
| `interim/` | Intermediate parse output. Regenerable. | no |
| `processed/` | Passages and derived datasets. Regenerable. | no |
| `cache/` | LLM/embedding caches keyed by model + prompt version + input hash. | no |
| `manifest.jsonl` | One record per acquired document: source, url, sha256, retrieved_at, license. | yes |

Raw files are never edited. If a source needs correction, record the correction as a
derived artifact and keep the original.

`manifest.jsonl` is committed because it is the provenance record: it lets an outside
reader verify which exact files produced a published result.

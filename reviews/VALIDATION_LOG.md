# VALIDATION LOG

日期：2026-09-16。以下结果均针对 `Xpert-Portfolio/extracted/` 副本，除非另有说明。

## Source inventory

- 本地项目：`01-mcp-workbench`、`02-qa-sentinel`、`03-data-cleanroom-studio`、`04-webhook-observatory`、`05-browserops-capture`、`06-document-pipeline-studio`。
- 重复的 `_clean_validation_06` 只作 D 类记录，不重复计入。
- 公开项目：Agentic GPU Optimizer、RAG Poisoning Detection、GPU Kernel Performance Lab、Spectral Operator GPU Lab、Scientific Reproducibility Kit 等；完整表见 `PROJECT_INVENTORY.md`。
- 未发现本轮授权可见的 itch 游戏目录或 Minecraft Mod 目录。

## Test / build evidence

| 副本 | 命令 | 结果 |
|---|---|---|
| `local/01-mcp-workbench` | `npm test` | 2 files, 14 passed |
| `local/01-mcp-workbench` | `npm run build` | exit 0 |
| `local/01-mcp-workbench` | `npm run test:e2e` | 2 passed |
| `local/02-qa-sentinel` | `npm test` | 1 file, 2 passed |
| `local/02-qa-sentinel` | `npm run build` | exit 0 |
| `local/02-qa-sentinel` | `npm run test:e2e` | 1 passed |
| `local/03-data-cleanroom-studio` | `npm test` | 9 passed |
| `local/03-data-cleanroom-studio` | build | exit 0 |
| `local/03-data-cleanroom-studio` | E2E | 1 passed |
| `local/04-webhook-observatory` | `npm test` | 4 files, 16 passed |
| `local/04-webhook-observatory` | `npm run build` | exit 0 |
| `local/04-webhook-observatory` | `npm run test:e2e` | 1 passed |
| `local/05-browserops-capture` | `npm test` | 5 files, 10 passed |
| `local/05-browserops-capture` | build | exit 0 |
| `local/05-browserops-capture` | E2E | 1 passed |
| `local/06-document-pipeline-studio/backend` | `pytest -q` | 12 passed, 5 warnings |
| `local/06-document-pipeline-studio/frontend` | build | exit 0 |
| `local/06-document-pipeline-studio/frontend` | E2E | 1 passed; proxy fallback logs observed |
| `public/agentic-gpu-optimizer` | `python -m pytest -q` | 8 passed |
| `public/agentic-gpu-optimizer` | `scripts/run_case_studies.py` | exit 0; transpose INCONCLUSIVE, reduction REJECT |
| `public/rag-poisoning-detection-trusted-provenance/backend` | `pytest -q` | 6 passed, 2 warnings |
| `public/scientific-reproducibility-kit` | `python -m pytest -q` | 4 passed |
| `public/scientific-reproducibility-kit` | demo + bundle validation | exit 0; validation JSON valid |

## PDF checks

- [x] artifact operation marked immediately before the first PDF authoring command.
- [x] V1 rendered to PDF and 10 PNG pages.
- [x] V1 visual review records 25 real issues in `DESIGN_REVIEW_V1.md`.
- [x] V2 rendered after fixes; final pages re-rendered from V2.
- [x] Final PDF has 10 pages, each 594.96 x 841.92 pt (A4 portrait).
- [x] Final PDF has 6 preserved public GitHub URI annotations.
- [x] PDF text extraction has 13,265 characters, no local path markers, no `.env`, private-key or GitHub-token markers, and no Unicode dash characters.
- [x] PDF metadata is scrubbed: Title `Xpert Technical Portfolio`, blank Author, Creator/Producer `Xpert Portfolio`; no username or local path.
- [x] Final PDF is 693,875 bytes, well below the requested 10 MB ceiling.
- [x] Final PDF page PNGs are in `FINAL/` as `Xpert_Portfolio_Page_01.png` ... `Page_10.png`.
- [x] Re-rendering the metadata-scrubbed final PDF produced 10 pages; all 10 PNG SHA-256 hashes match the published page previews.
- [x] Final PDF SHA-256: `CDD206BEDA46FC9925BBB35E57E54832E73833AC269BC23E6BC41CD11AA3BEA5`.

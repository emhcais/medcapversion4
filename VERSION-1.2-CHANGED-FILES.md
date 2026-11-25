# Version 1.2 changed files

This replacement package is based directly on Version 1.1. The following files differ from that package.

| File | Version 1.2 change |
|---|---|
| `index.html` | Updates the version title; removes the small Version 1.1 heading; removes the date-filter note; reorders and adds map options; checks documented connections by default; updates the guide. |
| `app.js` | Adds No Location Data behavior; restores documented connections on reset; uses the nine-field historical record order; separates Source and Notes; adds Ship Name; places the date-method note beneath Date; updates the guide-storage version. |
| `styles.css` | Gives both slider handles the same explicit color and opacity; changes the map-option grid from three to four controls; styles the small note beneath Date. |
| `scripts/prepare_data.py` | Generates Version 1.2 metadata and separate `source`, `notes`, and `ship_name` application fields from the original CSV columns. |
| `data/app-data.json` | Regenerated application data containing the separate Source, Notes, and Ship Name fields. |
| `data/build-report.json` | Regenerated Version 1.2 build metadata and validation counts. |
| `README.md` | Documents Version 1.2 behavior and data-field rules. |
| `GITHUB-NEXT-STEPS.md` | Updates upload instructions and acceptance checks for Version 1.2. |
| `CHANGELOG.md` | Adds the Version 1.2 release notes. |
| `VERSION-1.2-CHANGED-FILES.md` | New manifest identifying every file added or changed from Version 1.1. |
| `SHA256SUMS.txt` | Regenerated checksums for the complete replacement package. |

`data/european-captives-complete.csv` was regenerated from the supplied source CSV during the verified build, but its SHA-256 checksum is unchanged from Version 1.1. The interface changes do not alter the complete 3,137-row historical-data export.

Unchanged files are `.nojekyll`, `METHODOLOGY.md`, and `data/european-captives-complete.csv`.
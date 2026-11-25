# European Captives Map — Version 1.2

A browser-only Leaflet application for GitHub Pages. Version 1.2 is a targeted update to Version 1.1 and preserves its historical-atlas layout, colors, typography, navigation, and map treatment.

## What changed

- Documented connections are on when the map opens and after **Reset Filters**.
- The two time-slider handles use the same color and opacity.
- The map options appear as **Both / Origins / Captivity / No Location Data**.
- **No Location Data** keeps the map visible without markers and shows the searchable set of records with neither a documented origin nor a documented captivity location.
- Removed only the small `Mediterranean Captivity Project · Version 1.1` heading; the **European Captives** title remains.
- Moved the normalized-year/January 1 explanation from the filter area to a small note beneath **Date** in each historical record.
- Historical records now use this nine-field order: Name, Place of Origin, Place of Captivity, Convert, Date, Ship Name, Source, Notes, and Record ID.
- `Source` and `Notes` now display independently from their respective original CSV columns.

## Data behavior

The original CSV is not edited in place. The preparation script assigns a stable row-based Record ID and creates a separate mapping dataset.

For the concise record display, **Source** uses the original `Source` column and **Notes** uses the original `Notes` column. Missing values are labeled **Not documented** rather than being substituted across fields. **Ship Name** likewise uses its original CSV column.

Unknown locations are labeled **Not documented** in record details. They do not receive an artificial map marker. Named but unresolved origins remain searchable and available in the CSV. The **No Location Data** option is narrower: it lists only records for which both original location fields are undocumented.

January 1 values are treated as year-level entries for filtering. Six three-digit years (`617` and `624`) are normalized to 1617 and 1624 for filtering while the original date text remains visible.

## Files to upload to GitHub

Upload the **contents of this folder** so these items appear at the repository root:

- `index.html`
- `app.js`
- `styles.css`
- `data/`
- `scripts/`
- `.nojekyll`
- `README.md`
- `GITHUB-NEXT-STEPS.md`

No Python, terminal, build process, CARTO account, or API key is needed to publish or view the prepared map.

## Rebuilding after a future CSV update

The included preparation script uses only Python's standard library:

```bash
python3 scripts/prepare_data.py "BC Project Captivity Complete Location Date.csv" .
```

Visitors do not need Python; this command is only for a future maintainer who wants to regenerate the application data.

## External services

- Leaflet 1.9.4 is loaded from `unpkg.com`.
- Basemap tiles are loaded from OpenStreetMap and require no API key.
- An internet connection is required for the basemap and Leaflet CDN.

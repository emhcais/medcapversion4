# Methodology note

This map visualizes documented associations between records and places. It does not reconstruct unrecorded journeys.

- The 3,137 source rows are preserved as distinct records and receive sequential IDs (`EC000001`–`EC003137`).
- Unknown or `n/a` locations are not mapped.
- The 812 rows that used `35.9982, -5.6879` as a Strait of Gibraltar placeholder remain searchable but do not create markers or connections.
- Tripoli is mapped with a reviewed city-centre point instead of the spreadsheet's `#FIELD!` coordinate errors.
- Origins use a curated crosswalk. Ambiguous or unresolved labels remain in the record and CSV without a marker.
- January 1 values are treated as year-level entries for filtering.
- Marker size reflects the number of matching records at a location after search and date filters.
- Connection lines indicate records with both locations mapped; they are not travel routes.

The complete CSV preserves all original fields and adds record, date-normalization, and mapping-status fields so that the public map can be audited.

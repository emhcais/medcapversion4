#!/usr/bin/env python3
"""Prepare the European Captives Leaflet v1.2 data package.

Uses only Python's standard library. The source CSV is never modified.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

MISSING = {"", "n/a", "na", "none", "unknown", "not known", "null"}

CAPTIVITY = {
    "Algiers": (36.7538, 3.0588, "high", "Modern city centre"),
    "Tunis": (36.8065, 10.1815, "high", "Modern city centre"),
    "Marrakesh": (31.6295, -7.9811, "high", "Modern city centre"),
    "Tripoli": (32.8872, 13.1913, "high", "Corrected from spreadsheet #FIELD! error"),
    "Salé": (34.0531, -6.7985, "high", "Modern city centre"),
    "Tangier": (35.7595, -5.8340, "high", "Modern city centre"),
    "Meknes": (33.8730, -5.5407, "high", "Modern city centre"),
}

# Curated gazetteer. Ambiguous historical labels are either marked medium/low
# certainty or deliberately left unmapped. Coordinates are representative
# points, not reconstructed historical addresses.
ORIGINS = {
    "London": ("London", 51.5074, -0.1278, "high", "United Kingdom"),
    "Bristol": ("Bristol", 51.4545, -2.5879, "high", "United Kingdom"),
    "Plymouth": ("Plymouth", 50.3755, -4.1427, "high", "Devon, United Kingdom"),
    "Lisbon": ("Lisbon", 38.7223, -9.1393, "high", "Portugal"),
    "Baltimore": ("Baltimore", 51.4840, -9.3720, "medium", "Interpreted as Baltimore, County Cork, Ireland"),
    "New England": ("New England", 43.9650, -71.5300, "low", "Regional representative point; not a precise origin"),
    "Dartmouth": ("Dartmouth", 50.3525, -3.5794, "high", "Devon, United Kingdom"),
    "Portsmouth": ("Portsmouth", 50.8198, -1.0880, "high", "Hampshire, United Kingdom"),
    "Mahón": ("Mahón", 39.8885, 4.2658, "high", "Menorca, Spain"),
    "Barnstaple": ("Barnstaple", 51.0802, -4.0581, "high", "Devon, United Kingdom"),
    "Rochel": ("La Rochelle", 46.1603, -1.1511, "medium", "Historical spelling interpreted as La Rochelle, France"),
    "Gallipoli": ("Gallipoli", 40.0550, 17.9920, "low", "Interpreted as Gallipoli, Apulia, Italy; verify against source"),
    "Cádiz": ("Cádiz", 36.5297, -6.2927, "high", "Spain"),
    "Great Yarmouth": ("Great Yarmouth", 52.6084, 1.7305, "high", "Norfolk, United Kingdom"),
    "Weymouth": ("Weymouth", 50.6090, -2.4543, "high", "Dorset, United Kingdom"),
    "Dover": ("Dover", 51.1279, 1.3134, "high", "Kent, United Kingdom"),
    "St. Martin's": (None, None, None, "unresolved", "Multiple plausible places; retained in catalogue only"),
    "Amsterdam": ("Amsterdam", 52.3676, 4.9041, "high", "Netherlands"),
    "Alicante": ("Alicante", 38.3452, -0.4810, "high", "Spain"),
    "Tunis": ("Tunis", 36.8065, 10.1815, "high", "Tunisia"),
    "Newfoundland and Labrador": ("Newfoundland and Labrador", 53.1355, -57.6604, "low", "Regional representative point; not a precise origin"),
    "Split": ("Split", 43.5081, 16.4402, "high", "Croatia"),
    "Yahall": ("Youghal", 51.9517, -7.8456, "medium", "Historical spelling interpreted as Youghal, Ireland"),
    "St. Fillo": (None, None, None, "unresolved", "Historical label not confidently identified"),
    "Porto": ("Porto", 41.1579, -8.6291, "high", "Portugal"),
    "Apson": (None, None, None, "unresolved", "Historical label not confidently identified"),
    "Penzance": ("Penzance", 50.1188, -5.5376, "high", "Cornwall, United Kingdom"),
    "Terceras": ("Terceira", 38.7216, -27.2206, "medium", "Historical plural interpreted as Terceira/Azores; representative point"),
    "Topsham": ("Topsham", 50.6850, -3.4660, "high", "Devon, United Kingdom"),
    "Southampton": ("Southampton", 50.9097, -1.4044, "high", "United Kingdom"),
    "Exeter": ("Exeter", 50.7184, -3.5339, "high", "Devon, United Kingdom"),
    "Madeira": ("Madeira", 32.7607, -16.9595, "medium", "Regional representative point"),
    "Fowey": ("Fowey", 50.3363, -4.6386, "high", "Cornwall, United Kingdom"),
    "Waterford": ("Waterford", 52.2593, -7.1101, "high", "Ireland"),
    "Lyme Regis": ("Lyme Regis", 50.7266, -2.9348, "high", "Dorset, United Kingdom"),
    "Kinsale": ("Kinsale", 51.7059, -8.5222, "high", "Ireland"),
    "Bideford": ("Bideford", 51.0167, -4.2089, "high", "Devon, United Kingdom"),
    "Poole": ("Poole", 50.7151, -1.9872, "high", "Dorset, United Kingdom"),
    "Kingston upon Hull": ("Kingston upon Hull", 53.7676, -0.3274, "high", "United Kingdom"),
    "Falmouth": ("Falmouth", 50.1526, -5.0663, "high", "Cornwall, United Kingdom"),
    "North Yarmouth": ("Yarmouth", 50.7050, -1.5000, "low", "Interpreted as Yarmouth, Isle of Wight; verify against source"),
    "Edinburgh": ("Edinburgh", 55.9533, -3.1883, "high", "Scotland, United Kingdom"),
    "Low": (None, None, None, "unresolved", "Historical label not confidently identified"),
    "Bermuda": ("Bermuda", 32.3078, -64.7505, "medium", "Regional representative point"),
    "Sanlúcar de Barrameda": ("Sanlúcar de Barrameda", 36.7781, -6.3515, "high", "Spain"),
    "Boston": ("Boston", 52.9789, -0.0266, "low", "Interpreted as Boston, Lincolnshire; verify against source"),
    "New York City": ("New York City", 40.7128, -74.0060, "high", "New York, United States"),
    "Chester": ("Chester", 53.1934, -2.8931, "high", "United Kingdom"),
    "Cork": ("Cork", 51.8985, -8.4756, "high", "Ireland"),
    "Dublin": ("Dublin", 53.3498, -6.2603, "high", "Ireland"),
    "Rye": ("Rye", 50.9497, 0.7373, "high", "East Sussex, United Kingdom"),
    "Chatham": ("Chatham", 51.3811, 0.5269, "medium", "Interpreted as Chatham, Kent, United Kingdom"),
    "Lyn": ("King's Lynn", 52.7517, 0.3952, "low", "Interpreted as King's Lynn; verify against source"),
    "Feloe": (None, None, None, "unresolved", "Historical label not confidently identified"),
    "Bridgwater": ("Bridgwater", 51.1281, -3.0036, "high", "Somerset, United Kingdom"),
    "St.Urbes": (None, None, None, "unresolved", "Historical label not confidently identified"),
    "Millbrook": ("Millbrook", 50.3495, -4.2170, "low", "Interpreted as Millbrook, Cornwall; verify against source"),
    "Colchester": ("Colchester", 51.8959, 0.8919, "high", "Essex, United Kingdom"),
    "Brighton": ("Brighton", 50.8225, -0.1372, "high", "United Kingdom"),
    "Hampton": ("Hampton", 51.4211, -0.3697, "low", "Interpreted as Hampton, Middlesex; verify against source"),
    "Watchet": ("Watchet", 51.1817, -3.3290, "high", "Somerset, United Kingdom"),
    "Foulston": ("Folkestone", 51.0814, 1.1695, "low", "Possible historical spelling of Folkestone; verify against source"),
    "Dorset": ("Dorset", 50.7488, -2.3445, "medium", "County representative point"),
    "Worcester": ("Worcester", 52.1936, -2.2216, "high", "United Kingdom"),
    "Saltash": ("Saltash", 50.4096, -4.2251, "high", "Cornwall, United Kingdom"),
    "Sandwich": ("Sandwich", 51.2743, 1.3380, "high", "Kent, United Kingdom"),
    "Swansea": ("Swansea", 51.6214, -3.9436, "high", "Wales, United Kingdom"),
    "Sidmouth": ("Sidmouth", 50.6800, -3.2397, "high", "Devon, United Kingdom"),
    "Warom": (None, None, None, "unresolved", "Historical label not confidently identified"),
    "Christchurch": ("Christchurch", 50.7358, -1.7782, "medium", "Interpreted as Christchurch, Dorset"),
    "Liverpool": ("Liverpool", 53.4084, -2.9916, "high", "United Kingdom"),
    "Newcastle upon Tyne": ("Newcastle upon Tyne", 54.9783, -1.6178, "high", "United Kingdom"),
    "Dundee": ("Dundee", 56.4620, -2.9707, "high", "Scotland, United Kingdom"),
    "Ipswich": ("Ipswich", 52.0567, 1.1482, "high", "Suffolk, United Kingdom"),
    "Selborne": ("Selborne", 51.0960, -0.9410, "high", "Hampshire, United Kingdom"),
    "Harwich": ("Harwich", 51.9446, 1.2864, "high", "Essex, United Kingdom"),
    "Coleraine": ("Coleraine", 55.1330, -6.6680, "high", "Northern Ireland, United Kingdom"),
    "Stockton": ("Stockton-on-Tees", 54.5705, -1.3187, "low", "Interpreted as Stockton-on-Tees; verify against source"),
    "St. Martin Parish": ("Saint Martin", 49.4350, -2.5760, "low", "Interpreted as Saint Martin, Guernsey; verify against source"),
}


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def is_missing(value: str) -> bool:
    return clean(value).casefold() in MISSING


def parse_date(raw: str):
    value = clean(raw)
    if is_missing(value):
        return None, "unknown", "Date not documented", value
    corrected = value
    correction = ""
    if value == "01/01/617":
        corrected = "01/01/1617"
        correction = "Corrected from 617 to 1617 using the year written in the captive-name field."
    elif value == "01/01/624":
        corrected = "01/01/1624"
        correction = "Corrected from 624 to 1624 using the year written in the captive-name field."
    if re.fullmatch(r"\d{4}", corrected):
        return int(corrected), "year", correction or "Year only", value
    try:
        dt = datetime.strptime(corrected, "%m/%d/%Y")
    except ValueError:
        try:
            dt = datetime.strptime(corrected, "%m/%d/%y")
        except ValueError:
            return None, "unparsed", "Date retained as written; review required", value
    if dt.month == 1 and dt.day == 1:
        note = "Year only; 1 January is treated as a data-entry placeholder"
        if correction:
            note = correction + " " + note
        return dt.year, "year", note, value
    return dt.year, "day", correction or "Day-level date", value


def slug(value: str) -> str:
    text = clean(value).casefold()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "location"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source_csv", type=Path)
    ap.add_argument("output_dir", type=Path)
    args = ap.parse_args()
    data_dir = args.output_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    with args.source_csv.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        original_headers = reader.fieldnames or []

    name_header = next(h for h in original_headers if h.strip().startswith("Captive's Name"))
    locations = {}
    records = []
    export_rows = []
    placeholder_removed = 0

    def add_location(mapping_id, role, original, standard, lat, lon, certainty, note):
        locations[mapping_id] = {
            "mapping_id": mapping_id,
            "role": role,
            "original_label": original,
            "standardized_name": standard,
            "latitude": lat,
            "longitude": lon,
            "certainty": certainty,
            "review_note": note,
        }

    for i, row in enumerate(rows, start=1):
        record_id = f"EC{i:06d}"
        name = clean(row.get(name_header, "")) or "Name not documented"
        raw_date = clean(row.get("Date", ""))
        year, date_precision, date_note, _ = parse_date(raw_date)
        explicit_source = clean(row.get("Source", ""))
        notes = clean(row.get("Notes", ""))
        source_display = explicit_source if not is_missing(explicit_source) else "Not documented"
        notes_display = notes if not is_missing(notes) else "Not documented"
        ship_raw = clean(row.get("Ship Name", ""))
        ship_name = ship_raw if not is_missing(ship_raw) else "Not documented"
        origin_raw = clean(row.get("Place of Origin", ""))
        captivity_raw = clean(row.get("Place of Captivity", ""))
        convert = clean(row.get("Convert", "")) or "Not documented"

        origin_mapping_id = None
        origin_status = "unknown"
        origin_standard = ""
        origin_note = ""
        origin_lat = origin_lon = ""
        if not is_missing(origin_raw):
            cw = ORIGINS.get(origin_raw)
            if cw and cw[1] is not None:
                origin_standard, lat, lon, certainty, origin_note = cw
                origin_mapping_id = f"origin-{slug(origin_raw)}"
                origin_status = "mapped"
                origin_lat, origin_lon = lat, lon
                add_location(origin_mapping_id, "origin", origin_raw, origin_standard, lat, lon, certainty, origin_note)
            else:
                origin_status = "unmapped_named"
                origin_note = cw[4] if cw else "Named origin not in reviewed gazetteer"

        captivity_mapping_id = None
        captivity_status = "unknown"
        captivity_standard = ""
        captivity_note = ""
        captivity_lat = captivity_lon = ""
        if not is_missing(captivity_raw):
            cw = CAPTIVITY.get(captivity_raw)
            if cw:
                lat, lon, certainty, captivity_note = cw
                captivity_standard = captivity_raw
                captivity_mapping_id = f"captivity-{slug(captivity_raw)}"
                captivity_status = "mapped"
                captivity_lat, captivity_lon = lat, lon
                add_location(captivity_mapping_id, "captivity", captivity_raw, captivity_standard, lat, lon, certainty, captivity_note)
            else:
                captivity_status = "unmapped_named"
                captivity_note = "Named captivity place not in reviewed gazetteer"
        elif clean(row.get("Lat_C", "")) == "35.9982" and clean(row.get("Long_C", "")) == "-5.6879":
            placeholder_removed += 1

        if origin_mapping_id and captivity_mapping_id:
            geography_status = "both"
        elif origin_mapping_id:
            geography_status = "origin_only"
        elif captivity_mapping_id:
            geography_status = "captivity_only"
        else:
            geography_status = "neither"

        search_values = [
            record_id, name, raw_date, year or "", date_note, explicit_source, notes,
            origin_raw, origin_standard, captivity_raw, captivity_standard, convert,
            clean(row.get("Total", "")), clean(row.get("Gender", "")), clean(row.get("Ship Name", "")),
        ]
        records.append({
            "record_id": record_id,
            "name": name,
            "date": raw_date if not is_missing(raw_date) else "Not documented",
            "year": year,
            "date_note": date_note,
            "source": source_display,
            "notes": notes_display,
            "ship_name": ship_name,
            "place_of_origin": origin_raw if not is_missing(origin_raw) else "Not documented",
            "place_of_captivity": captivity_raw if not is_missing(captivity_raw) else "Not documented",
            "convert": convert,
            "origin_mapping_id": origin_mapping_id,
            "captivity_mapping_id": captivity_mapping_id,
            "geography_status": geography_status,
            "search_text": " ".join(str(v) for v in search_values).casefold(),
        })

        cleaned_original = {h.strip(): clean(row.get(h, "")) for h in original_headers}
        cleaned_original.update({
            "Record ID": record_id,
            "Year": year if year is not None else "",
            "Date Precision": date_precision,
            "Date Note": date_note,
            "Origin Mapping Status": origin_status,
            "Origin Standard Name": origin_standard,
            "Origin Latitude": origin_lat,
            "Origin Longitude": origin_lon,
            "Origin Mapping Note": origin_note,
            "Captivity Mapping Status": captivity_status,
            "Captivity Standard Name": captivity_standard,
            "Captivity Latitude": captivity_lat,
            "Captivity Longitude": captivity_lon,
            "Captivity Mapping Note": captivity_note,
        })
        export_rows.append(cleaned_original)

    years = [r["year"] for r in records if r["year"] is not None]
    geography_counts = defaultdict(int)
    for record in records:
        geography_counts[record["geography_status"]] += 1
    metadata = {
        "title": "European Captives Map Version 1.2",
        "generated_from": args.source_csv.name,
        "source_rows": len(rows),
        "records": len(records),
        "minimum_year": min(years),
        "maximum_year": max(years),
        "mappable_locations": len(locations),
        "geography_counts": dict(geography_counts),
        "records_without_documented_location": sum(
            1 for r in records
            if r["place_of_origin"] == "Not documented" and r["place_of_captivity"] == "Not documented"
        ),
        "strait_placeholder_records_removed": placeholder_removed,
        "method_note": "Unknown locations are excluded from the map but retained in search and the complete CSV.",
    }
    app_data = {"metadata": metadata, "locations": locations, "records": records}
    (data_dir / "app-data.json").write_text(
        json.dumps(app_data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )

    export_headers = list(export_rows[0].keys()) if export_rows else []
    with (data_dir / "european-captives-complete.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=export_headers)
        writer.writeheader()
        writer.writerows(export_rows)

    report = {
        **metadata,
        "records_with_mapped_origin": sum(1 for r in records if r["origin_mapping_id"]),
        "records_with_mapped_captivity": sum(1 for r in records if r["captivity_mapping_id"]),
        "records_with_both_mapped": sum(1 for r in records if r["origin_mapping_id"] and r["captivity_mapping_id"]),
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
    }
    (data_dir / "build-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

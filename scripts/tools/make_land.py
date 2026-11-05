"""Rasterize Natural Earth land (minus big lakes) into scripts/data/land.txt.

Usage: python3 -I scripts/tools/make_land.py ne_110m_land.geojson ne_110m_lakes.geojson
Source: Natural Earth 1:110m (public domain), github.com/nvkelso/natural-earth-vector.
Output: equirectangular mask, 2° per cell, 90 rows (90N→90S) × 180 cols (180W→180E), '#' = land.
"""
import json
import sys
from pathlib import Path

STEP = 2
OUT = Path(__file__).resolve().parent.parent / "data" / "land.txt"


def rings(path: str, min_area: float = 0.0) -> list:
    out = []
    for feature in json.loads(Path(path).read_text(encoding="utf-8"))["features"]:
        geom = feature["geometry"]
        polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        for poly in polys:
            for ring in poly:
                xs = [p[0] for p in ring]
                ys = [p[1] for p in ring]
                if (max(xs) - min(xs)) * (max(ys) - min(ys)) >= min_area:
                    out.append(ring)
    return out


def crossings(all_rings: list, lat: float) -> list:
    xs = []
    for ring in all_rings:
        for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
            if (y1 > lat) != (y2 > lat):
                xs.append(x1 + (lat - y1) * (x2 - x1) / (y2 - y1))
    return sorted(xs)


def inside(xs: list, lon: float) -> bool:
    return sum(1 for x in xs if x < lon) % 2 == 1


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 1
    land, lakes = rings(sys.argv[1]), rings(sys.argv[2], min_area=4.0)
    rows = []
    for r in range(180 // STEP):
        lat = 90 - STEP / 2 - r * STEP
        land_x, lake_x = crossings(land, lat), crossings(lakes, lat)
        row = ""
        for c in range(360 // STEP):
            lon = -180 + STEP / 2 + c * STEP
            row += "#" if inside(land_x, lon) and not inside(lake_x, lon) else "."
        rows.append(row)
    OUT.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"land: {OUT} ({len(rows)}x{len(rows[0])}, {sum(r.count('#') for r in rows)} land cells)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

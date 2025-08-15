# src/fll_sim/scripts/fetch_all_mats.py
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml
except Exception:  # noqa: BLE001
    print(
        "Missing dependency: PyYAML. Install with: pip install pyyaml",
        file=sys.stderr,
    )
    raise

from .fetch_mat import fetch_mat_image, fetch_mat_pdf


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Download FLL mat images from a user-provided manifest."
        )
    )
    p.add_argument(
        "--manifest",
        required=True,
        help="YAML file with seasons and URLs.",
    )
    p.add_argument(
        "--repo-root",
        default=None,
        help="Repo root (defaults to project root).",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = (
        Path(args.repo_root)
        if args.repo_root
        else Path(__file__).resolve().parents[3]
    )
    mats_dir = repo_root / "assets" / "mats"
    mats_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = Path(args.manifest)
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))

    count = 0
    for entry in data:
        season = entry.get("season")
        url = entry.get("url")
        kind = entry.get("type", entry.get("format", "image")).lower()
        page = int(entry.get("page", 0))
        dpi = int(entry.get("dpi", 300))
        page_label = entry.get("page_label")
        toc_title = entry.get("toc_title")
        if not season or not url:
            print(f"Skipping invalid entry: {entry}")
            continue
        out_dir = mats_dir / season
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / "mat.png"
        print(f"Downloading {season} from {url} (type={kind}) ...")
        if kind == "pdf":
            fetch_mat_pdf(
                url,
                out_file,
                page=page,
                dpi=dpi,
                page_label=page_label,
                toc_title=toc_title,
            )
        else:
            fetch_mat_image(url, out_file)
        count += 1

    print(f"Downloaded {count} mats into {mats_dir}")


if __name__ == "__main__":  # pragma: no cover
    main()

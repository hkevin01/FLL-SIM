from __future__ import annotations

from pathlib import Path

from fll_sim.assets.mats import (get_mat_for_season, list_local_mat_images,
                                 pick_latest)


def _touch(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"x")


def test_pick_latest_simple() -> None:
    seasons = [
        "2023-masterpiece",
        "2024-submerged",
        "2021-cargoconnect",
    ]
    assert pick_latest(seasons) == "2024-submerged"


def test_get_mat_for_season_latest(tmp_path: Path) -> None:
    repo_root = tmp_path
    # Create fake mats directory
    mats = repo_root / "assets" / "mats"
    _touch(mats / "2023-masterpiece" / "mat.png")
    _touch(mats / "2024-submerged" / "mat.png")

    # No season specified -> latest
    img, w, h, resolved = get_mat_for_season(repo_root, None)
    assert resolved == "2024-submerged"
    assert img == mats / "2024-submerged" / "mat.png"
    assert isinstance(w, float) and isinstance(h, float)

    # Explicit latest
    img2, _, _, resolved2 = get_mat_for_season(repo_root, "latest")
    assert resolved2 == "2024-submerged"
    assert img2 == img

    # Explicit season
    img3, _, _, resolved3 = get_mat_for_season(repo_root, "2023-masterpiece")
    assert resolved3 == "2023-masterpiece"
    assert img3 == mats / "2023-masterpiece" / "mat.png"


def test_list_local_mat_images(tmp_path: Path) -> None:
    repo_root = tmp_path
    mats = repo_root / "assets" / "mats"
    _touch(mats / "2022-superpowered" / "mat.jpg")
    _touch(mats / "2021-cargoconnect" / "mat.jpeg")
    _touch(mats / "2024-submerged" / "mat.png")

    found = list_local_mat_images(repo_root)
    assert set(found.keys()) == {
        "2022-superpowered",
        "2021-cargoconnect",
        "2024-submerged",
    }

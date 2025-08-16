from __future__ import annotations

from pathlib import Path
import threading


def test_filename_rounding_and_generation(tmp_path: Path):
    from sharepoint_sim.service import SharePointCSVGenerator  # type: ignore[attr-defined]
    svc = SharePointCSVGenerator(root_dir=tmp_path, seed=123)
    out = svc.generate("ACQ", rows=12)
    assert out.exists()
    assert out.name.startswith("ACQ__") and out.name.endswith(".csv")
    parts = out.name.split("__")[1].removesuffix(".csv")
    date_part, time_part = parts.split("_")
    assert len(time_part) == 4 and time_part.isdigit()
    minute = int(time_part[2:])
    assert minute % 5 == 0


def test_deterministic_across_instances(tmp_path: Path):
    from sharepoint_sim.service import SharePointCSVGenerator  # type: ignore[attr-defined]
    svc1 = SharePointCSVGenerator(root_dir=tmp_path / "a", seed=999)
    p1 = svc1.generate("ACQ", rows=10)
    text1 = p1.read_text()
    svc2 = SharePointCSVGenerator(root_dir=tmp_path / "b", seed=999)
    p2 = svc2.generate("ACQ", rows=10)
    text2 = p2.read_text()
    assert text1 == text2


def test_concurrent_generation_locking(tmp_path: Path):
    from sharepoint_sim.service import SharePointCSVGenerator  # type: ignore[attr-defined]
    svc = SharePointCSVGenerator(root_dir=tmp_path, seed=42)
    paths: list[Path] = []

    def worker():
        paths.append(svc.generate("ACQ", rows=11))

    threads = [threading.Thread(target=worker) for _ in range(5)]
    for t in threads: t.start()
    for t in threads: t.join()
    assert len(paths) == 5
    existing = [p for p in set(paths) if p.exists()]
    assert existing
    assert existing[0].stat().st_size > 0

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a rough page-region manifest from a UX prototype image."
    )
    parser.add_argument("image", help="Path to the prototype image")
    parser.add_argument(
        "--ocr",
        choices=["auto", "none", "tesseract"],
        default="auto",
        help="Optional OCR backend. Falls back gracefully when unavailable.",
    )
    return parser.parse_args()


def average_rgb(samples: list[tuple[int, int, int]]) -> tuple[int, int, int]:
    if not samples:
        return (255, 255, 255)
    count = len(samples)
    return tuple(sum(pixel[i] for pixel in samples) // count for i in range(3))


def color_distance(a: tuple[int, int, int], b: tuple[int, int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])


def coarse_components(mask: list[list[bool]]) -> list[tuple[int, int, int, int, int]]:
    height = len(mask)
    width = len(mask[0]) if height else 0
    seen = [[False for _ in range(width)] for _ in range(height)]
    components: list[tuple[int, int, int, int, int]] = []

    for y in range(height):
        for x in range(width):
            if not mask[y][x] or seen[y][x]:
                continue
            stack = [(x, y)]
            seen[y][x] = True
            min_x = max_x = x
            min_y = max_y = y
            area = 0

            while stack:
                cx, cy = stack.pop()
                area += 1
                min_x = min(min_x, cx)
                max_x = max(max_x, cx)
                min_y = min(min_y, cy)
                max_y = max(max_y, cy)

                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if 0 <= nx < width and 0 <= ny < height and mask[ny][nx] and not seen[ny][nx]:
                        seen[ny][nx] = True
                        stack.append((nx, ny))

            components.append((min_x, min_y, max_x, max_y, area))

    return components


def detect_regions(image_path: Path) -> dict:
    notes: list[str] = []
    try:
        from PIL import Image
    except ImportError:
        return {
            "image": str(image_path),
            "notes": [
                "Pillow is not installed, so only path-level metadata is available.",
                "Install Pillow to enable auto page-region detection.",
            ],
            "regions": [],
        }

    image = Image.open(image_path).convert("RGB")
    width, height = image.size
    scale = min(1.0, 256.0 / max(width, height))
    downsampled = image.resize((max(1, int(width * scale)), max(1, int(height * scale))))
    small_width, small_height = downsampled.size

    sample_points = []
    corner_points = [
        (0, 0),
        (small_width - 1, 0),
        (0, small_height - 1),
        (small_width - 1, small_height - 1),
    ]
    for x, y in corner_points:
        sample_points.append(downsampled.getpixel((x, y)))
    for x in range(0, small_width, max(1, small_width // 12)):
        sample_points.append(downsampled.getpixel((x, 0)))
        sample_points.append(downsampled.getpixel((x, small_height - 1)))
    for y in range(0, small_height, max(1, small_height // 12)):
        sample_points.append(downsampled.getpixel((0, y)))
        sample_points.append(downsampled.getpixel((small_width - 1, y)))

    bg = average_rgb(sample_points)
    threshold = 48
    mask = []
    for y in range(small_height):
        row = []
        for x in range(small_width):
            pixel = downsampled.getpixel((x, y))
            row.append(color_distance(pixel, bg) > threshold)
        mask.append(row)

    # Remove tiny speckles that are usually guide text or compression noise.
    cleaned_mask = []
    for y in range(small_height):
        cleaned_row = []
        for x in range(small_width):
            if not mask[y][x]:
                cleaned_row.append(False)
                continue
            neighbors = 0
            for nx in range(max(0, x - 1), min(small_width, x + 2)):
                for ny in range(max(0, y - 1), min(small_height, y + 2)):
                    if mask[ny][nx]:
                        neighbors += 1
            cleaned_row.append(neighbors >= 4)
        cleaned_mask.append(cleaned_row)

    total_area = small_width * small_height
    regions = []
    for index, component in enumerate(coarse_components(cleaned_mask), start=1):
        min_x, min_y, max_x, max_y, area = component
        box_width = max_x - min_x + 1
        box_height = max_y - min_y + 1
        if area < total_area * 0.004:
            continue
        if box_width < 16 or box_height < 16:
            continue

        scaled_bbox = {
            "left": round(min_x / scale),
            "top": round(min_y / scale),
            "right": round((max_x + 1) / scale),
            "bottom": round((max_y + 1) / scale),
            "width": round(box_width / scale),
            "height": round(box_height / scale),
        }
        kind = "candidate_screen" if area >= total_area * 0.02 else "annotation_or_small_panel"
        regions.append(
            {
                "id": f"region_{index:02d}",
                "kind": kind,
                "bbox": scaled_bbox,
                "area_ratio": round(area / total_area, 4),
            }
        )

    regions.sort(key=lambda item: (item["bbox"]["top"], item["bbox"]["left"]))
    notes.append("Regions are heuristic visual blocks, not final page names.")
    notes.append("Use model vision to label each region as page, popup, mode switch, or annotation.")

    return {
        "image": str(image_path),
        "size": {"width": width, "height": height},
        "background_rgb": {"r": bg[0], "g": bg[1], "b": bg[2]},
        "regions": regions,
        "notes": notes,
    }


def try_ocr(image_path: Path, mode: str) -> dict:
    if mode == "none":
        return {"backend": "disabled", "lines": []}

    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        return {"backend": "unavailable", "lines": []}

    image = Image.open(image_path)
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    lines = []
    for text, confidence in zip(data.get("text", []), data.get("conf", [])):
        cleaned = " ".join((text or "").split())
        if not cleaned:
            continue
        try:
            score = float(confidence)
        except (TypeError, ValueError):
            score = -1
        if score < 40:
            continue
        lines.append({"text": cleaned, "confidence": round(score, 1)})
        if len(lines) >= 40:
            break
    return {"backend": "pytesseract", "lines": lines}


def main() -> int:
    args = parse_args()
    image_path = Path(args.image)
    payload = detect_regions(image_path)
    payload["ocr"] = try_ocr(image_path, args.ocr)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

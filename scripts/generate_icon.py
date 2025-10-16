import sys
from pathlib import Path

from PIL import Image


def generate_multi_size_ico(source_path: Path, output_path: Path) -> None:
    """Generate a multi-resolution .ico file from a source image.

    The output icon will embed common Windows sizes so Explorer always shows
    the custom icon regardless of thumbnail size.
    """
    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

    image = Image.open(source_path).convert("RGBA")

    # Pillow uses the first image and resizes to requested sizes on save
    # Ensure the source is large enough for quality downscales
    if max(image.size) < 256:
        # Upscale once to 256 for better resampling to smaller sizes
        image = image.resize((256, 256), Image.LANCZOS)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path, sizes=sizes)


def main(argv: list[str]) -> int:
    repo_root = Path(__file__).resolve().parents[1]
    default_src = repo_root / "assets" / "icons" / "ennead_architects_logo.ico"
    default_out = repo_root / "assets" / "icons" / "app_icon_multi.ico"

    src = Path(argv[1]) if len(argv) > 1 else default_src
    out = Path(argv[2]) if len(argv) > 2 else default_out

    if not src.exists():
        print(f"Source icon/image not found: {src}")
        return 1

    generate_multi_size_ico(src, out)
    print(f"Wrote multi-size icon: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))



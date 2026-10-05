from __future__ import annotations

from datetime import datetime
from pathlib import Path

SKIP_DIRS = {
    "__pycache__",
    ".pytest_cache",
    ".git",
    ".idea",
    ".venv",
    "venv",
}

MAX_PART_SIZE_BYTES = 100 * 1024

REPO_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_DIR = (
    REPO_ROOT
    / "artifacts"
    / "context"
)

OUTPUT_PREFIX = "alhf_full_repository_snapshot"


def should_skip(path: Path) -> bool:
    return any(
        part in SKIP_DIRS
        for part in path.parts
    )


def collect_files() -> list[Path]:
    files: list[Path] = []

    for root_name in ("src", "tests"):
        root = REPO_ROOT / root_name

        if not root.exists():
            continue

        for file_path in root.rglob("*"):
            if not file_path.is_file():
                continue

            if should_skip(file_path):
                continue

            files.append(file_path)

    return sorted(files)


def build_file_block(
    file_path: Path,
) -> list[str]:

    relative_path = file_path.relative_to(REPO_ROOT)

    block: list[str] = []

    block.append("")
    block.append("#" * 100)
    block.append(
        f"FILE: {relative_path}"
    )
    block.append("#" * 100)
    block.append("")

    try:
        content = file_path.read_text(
            encoding="utf-8",
            errors="ignore",
        )
    except Exception as ex:
        block.append(
            f"ERROR READING FILE: {ex}"
        )
        block.append("")
        return block

    block.append("```")
    block.append(content)
    block.append("```")
    block.append("")

    return block

def get_size_bytes(
    lines: list[str],
) -> int:
    return len(
        "\n".join(lines).encode("utf-8")
    )


def build_header(
    files: list[Path],
) -> list[str]:

    lines: list[str] = []

    lines.append(
        "# ALHF FULL REPOSITORY SNAPSHOT"
    )
    lines.append("")

    lines.append(
        f"Generated: {datetime.now()}"
    )
    lines.append("")

    lines.append(
        f"Total Files: {len(files)}"
    )
    lines.append("")

    lines.append(
        "=" * 100
    )
    lines.append(
        "REPOSITORY TREE"
    )
    lines.append(
        "=" * 100
    )
    lines.append("")

    for file_path in files:
        lines.append(
            str(
                file_path.relative_to(
                    REPO_ROOT
                )
            )
        )

    lines.append("")
    lines.append(
        "=" * 100
    )
    lines.append(
        "COMPLETE FILE CONTENTS"
    )
    lines.append(
        "=" * 100
    )
    lines.append("")

    return lines


def write_part(
    part_number: int,
    lines: list[str],
) -> Path:

    output_file = (
        OUTPUT_DIR
        / (
            f"{OUTPUT_PREFIX}"
            f"_part_{part_number:03d}.md"
        )
    )

    output_file.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    return output_file


def generate_snapshot() -> None:

    files = collect_files()

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    header = build_header(files)

    generated_files: list[Path] = []

    current_lines = header.copy()

    part_number = 1

    for file_path in files:

        block = build_file_block(
            file_path
        )

        block_size = get_size_bytes(block)

        if block_size > MAX_PART_SIZE_BYTES:
            print(
                f"WARNING: "
                f"{file_path.relative_to(REPO_ROOT)} "
                f"produces block larger than "
                f"{MAX_PART_SIZE_BYTES} bytes"
            )

        projected_size = get_size_bytes(
            current_lines + block
        )

        if (
            projected_size > MAX_PART_SIZE_BYTES
            and current_lines != header
        ):

            generated_files.append(
                write_part(
                    part_number,
                    current_lines,
                )
            )

            part_number += 1

            current_lines = header.copy()

        current_lines.extend(block)

    if current_lines:

        generated_files.append(
            write_part(
                part_number,
                current_lines,
            )
        )

    print(
        f"Generated {len(generated_files)} snapshot files"
    )

    print()

    for output_file in generated_files:
        size_kb = (
            output_file.stat().st_size
            / 1024
        )

        print(
            f"{output_file.name} "
            f"({size_kb:.2f} KB)"
        )

    print()
    print(
        f"Files dumped: {len(files)}"
    )


if __name__ == "__main__":
    generate_snapshot()

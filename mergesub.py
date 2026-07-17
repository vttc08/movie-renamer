"""Merge two SRT files into a bilingual ``mul.srt`` subtitle."""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable

import pysubs2


_BR_TAG = re.compile(r"<br\s*/?>", re.IGNORECASE)
_INTERNAL_LINE_BREAK = re.compile(r"(?:\\[Nn]|\r\n?|\n)+")
_WHITESPACE = re.compile(r"\s+")


@dataclass(frozen=True)
class SourceCue:
    """A normalized subtitle cue with its input ordering."""

    start: int
    end: int
    text: str
    source_index: int
    cue_index: int

    @property
    def key(self) -> tuple[int, int]:
        return self.source_index, self.cue_index


def _flatten_text(text: str) -> str:
    """Turn every cue into one line while retaining its formatting tags."""

    text = _INTERNAL_LINE_BREAK.sub(" ", text)
    return _WHITESPACE.sub(" ", text).strip()


def _load_cues(path: Path, source_index: int) -> list[SourceCue]:
    # pysubs2's SRT reader discards <br> tags, so replace them with spaces
    # before parsing to avoid accidentally joining the surrounding words.
    raw_srt = path.read_text(encoding="utf-8-sig")
    subtitles = pysubs2.SSAFile.from_string(
        _BR_TAG.sub(" ", raw_srt),
        format_="srt",
    )

    cues = []
    for cue_index, event in enumerate(subtitles):
        # Match srtmerge's half-open interval test: start <= point < end.
        # A cue with no positive duration can never appear in that model.
        if event.end <= event.start:
            continue
        cues.append(
            SourceCue(
                start=event.start,
                end=event.end,
                text=_flatten_text(event.text),
                source_index=source_index,
                cue_index=cue_index,
            )
        )
    return cues


def merge_cues(cues: Iterable[SourceCue]) -> pysubs2.SSAFile:
    """Merge normalized cues using every start/end time as a boundary."""

    starts: dict[int, list[SourceCue]] = defaultdict(list)
    ends: dict[int, list[SourceCue]] = defaultdict(list)

    for cue in cues:
        starts[cue.start].append(cue)
        ends[cue.end].append(cue)

    points = sorted(set(starts) | set(ends))
    active: dict[tuple[int, int], SourceCue] = {}
    merged = pysubs2.SSAFile()

    for point, next_point in zip(points, points[1:]):
        # End first because cues are inactive at their exact end timestamp.
        for cue in ends.get(point, ()):
            active.pop(cue.key, None)
        for cue in starts.get(point, ()):
            active[cue.key] = cue

        if not active or next_point <= point:
            continue

        ordered = sorted(
            active.values(),
            key=lambda cue: (cue.source_index, cue.cue_index),
        )
        text_by_source: dict[int, list[str]] = defaultdict(list)
        for cue in ordered:
            text_by_source[cue.source_index].append(cue.text)

        # A source can occasionally contain overlapping cues. Keep those on
        # the same physical line so two input files still produce at most two.
        lines = [
            " ".join(text for text in source_texts if text)
            for source_texts in text_by_source.values()
        ]
        merged.events.append(
            pysubs2.SSAEvent(
                start=point,
                end=next_point,
                text="\\N".join(lines),
            )
        )

    return merged


def merge_subtitles(
    first_subtitle: str | Path,
    second_subtitle: str | Path,
    output: str | Path | None = None,
) -> Path:
    """Merge two SRT paths and return the generated output path."""

    first_path = Path(first_subtitle)
    second_path = Path(second_subtitle)
    output_path = Path(output) if output is not None else first_path.parent / "mul.srt"

    for path in (first_path, second_path):
        if not path.is_file():
            raise FileNotFoundError(f"Subtitle file does not exist: {path}")
        if path.suffix.lower() != ".srt":
            raise ValueError(f"Only SRT inputs are supported: {path}")

    output_resolved = output_path.resolve()
    if output_resolved in (first_path.resolve(), second_path.resolve()):
        raise ValueError("Output path must not overwrite either input subtitle")

    cues = [
        *_load_cues(first_path, source_index=0),
        *_load_cues(second_path, source_index=1),
    ]
    merged = merge_cues(cues)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    merged.save(output_path, encoding="utf-8", format_="srt")
    return output_path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Merge two SRT files. Text from the first input is placed above "
            "text from the second input."
        )
    )
    parser.add_argument("first_subtitle", help="First (top-line) SRT file")
    parser.add_argument("second_subtitle", help="Second (bottom-line) SRT file")
    parser.add_argument(
        "-o",
        "--output",
        help="Output path (default: mul.srt beside the first input)",
    )
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    output_path = merge_subtitles(
        args.first_subtitle,
        args.second_subtitle,
        args.output,
    )
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

import tempfile
import textwrap
import unittest
from pathlib import Path

import pysubs2

from mergesub import merge_subtitles


def write_srt(path: Path, contents: str) -> None:
    path.write_text(textwrap.dedent(contents).strip() + "\n", encoding="utf-8")


class MergeSubtitlesTests(unittest.TestCase):
    def test_merges_matching_cues_in_input_order_and_flattens_lines(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            english = root / "en.srt"
            chinese = root / "zh.srt"
            write_srt(
                english,
                """
                1
                00:00:00,000 --> 00:00:02,000
                <i>Hello</i>
                there
                """,
            )
            write_srt(
                chinese,
                """
                1
                00:00:00,000 --> 00:00:02,000
                你好<br>世界
                """,
            )

            output = merge_subtitles(english, chinese)

            self.assertEqual(output, root / "mul.srt")
            merged = pysubs2.load(output, encoding="utf-8")
            self.assertEqual(len(merged), 1)
            self.assertEqual(merged[0].plaintext, "Hello there\n你好 世界")
            self.assertIn("<i>Hello</i> there", output.read_text(encoding="utf-8"))

    def test_splits_output_at_every_overlap_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            english = root / "en.srt"
            chinese = root / "zh.srt"
            write_srt(
                english,
                """
                1
                00:00:00,000 --> 00:00:10,000
                Hello
                """,
            )
            write_srt(
                chinese,
                """
                1
                00:00:02,000 --> 00:00:08,000
                你好
                """,
            )

            output = merge_subtitles(english, chinese)
            merged = pysubs2.load(output, encoding="utf-8")

            self.assertEqual(
                [(event.start, event.end, event.plaintext) for event in merged],
                [
                    (0, 2_000, "Hello"),
                    (2_000, 8_000, "Hello\n你好"),
                    (8_000, 10_000, "Hello"),
                ],
            )

    def test_end_timestamp_is_not_treated_as_overlapping(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            english = root / "en.srt"
            chinese = root / "zh.srt"
            write_srt(
                english,
                """
                1
                00:00:00,000 --> 00:00:01,000
                Hello
                """,
            )
            write_srt(
                chinese,
                """
                1
                00:00:01,000 --> 00:00:02,000
                你好
                """,
            )

            output = merge_subtitles(english, chinese)
            merged = pysubs2.load(output, encoding="utf-8")

            self.assertEqual(
                [(event.start, event.end, event.plaintext) for event in merged],
                [(0, 1_000, "Hello"), (1_000, 2_000, "你好")],
            )

    def test_overlapping_cues_from_one_source_stay_on_one_line(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            english = root / "en.srt"
            chinese = root / "zh.srt"
            write_srt(
                english,
                """
                1
                00:00:00,000 --> 00:00:02,000
                Hello

                2
                00:00:00,000 --> 00:00:02,000
                there
                """,
            )
            write_srt(
                chinese,
                """
                1
                00:00:00,000 --> 00:00:02,000
                你好
                """,
            )

            output = merge_subtitles(english, chinese)
            merged = pysubs2.load(output, encoding="utf-8")

            self.assertEqual(merged[0].plaintext, "Hello there\n你好")


if __name__ == "__main__":
    unittest.main()

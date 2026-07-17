import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest.mock import patch

import pysubs2

from mergesub import merge_subtitles, remove_short_transition_runs


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

    def test_merge_pipeline_removes_short_transition_fragments(self) -> None:
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
                """,
            )
            write_srt(
                chinese,
                """
                1
                00:00:00,200 --> 00:00:01,800
                你好
                """,
            )

            output = merge_subtitles(english, chinese)
            merged = pysubs2.load(output, encoding="utf-8")

            self.assertEqual(
                [(event.start, event.end, event.plaintext) for event in merged],
                [(200, 1_800, "Hello\n你好")],
            )

    def test_accepts_uppercase_srt_extension(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            english = root / "en.SRT"
            chinese = root / "zh.SRT"
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
                00:00:00,000 --> 00:00:01,000
                你好
                """,
            )

            output = merge_subtitles(english, chinese)

            self.assertTrue(output.is_file())

    def test_rejects_wrong_extension_before_reading_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            movie = root / "movie.mkv"
            chinese = root / "zh.srt"
            movie.write_bytes(b"not a subtitle")
            write_srt(
                chinese,
                """
                1
                00:00:00,000 --> 00:00:01,000
                你好
                """,
            )

            with patch.object(
                Path,
                "read_text",
                side_effect=AssertionError("input content was read"),
            ):
                with self.assertRaisesRegex(ValueError, "Only SRT"):
                    merge_subtitles(chinese, movie)

    def test_rejects_oversized_input_before_reading_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            english = root / "en.srt"
            chinese = root / "zh.srt"
            english.write_bytes(b"x")
            chinese.write_bytes(b"too large")

            with (
                patch("mergesub.MAX_INPUT_SIZE_BYTES", 5),
                patch.object(
                    Path,
                    "read_text",
                    side_effect=AssertionError("input content was read"),
                ),
            ):
                with self.assertRaisesRegex(ValueError, "input limit"):
                    merge_subtitles(english, chinese)

    def test_invalid_content_does_not_replace_existing_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            english = root / "en.srt"
            chinese = root / "zh.srt"
            output = root / "mul.srt"
            english.write_bytes(b"\xff\xfe\x00")
            write_srt(
                chinese,
                """
                1
                00:00:00,000 --> 00:00:01,000
                你好
                """,
            )
            output.write_text("existing output", encoding="utf-8")

            with self.assertRaises(UnicodeDecodeError):
                merge_subtitles(english, chinese)

            self.assertEqual(output.read_text(encoding="utf-8"), "existing output")

    def test_cueless_input_does_not_replace_existing_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            english = root / "en.srt"
            chinese = root / "zh.srt"
            output = root / "mul.srt"
            english.write_text("not an SRT", encoding="utf-8")
            write_srt(
                chinese,
                """
                1
                00:00:00,000 --> 00:00:01,000
                你好
                """,
            )
            output.write_text("existing output", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "no positive-duration cues"):
                merge_subtitles(english, chinese)

            self.assertEqual(output.read_text(encoding="utf-8"), "existing output")


class RemoveShortTransitionRunsTests(unittest.TestCase):
    @staticmethod
    def subtitles(*events: tuple[int, int, str]) -> pysubs2.SSAFile:
        subtitles = pysubs2.SSAFile()
        subtitles.events = [
            pysubs2.SSAEvent(start=start, end=end, text=text)
            for start, end, text in events
        ]
        return subtitles

    def test_removes_short_contiguous_transition_run(self) -> None:
        subtitles = self.subtitles(
            (0, 1_000, "Hello\\N你好"),
            (1_000, 1_200, "你好"),
            (1_200, 1_400, "Goodbye\\N你好"),
            (1_400, 2_400, "Goodbye\\N再见"),
        )

        cleaned = remove_short_transition_runs(subtitles)

        self.assertEqual(
            [(event.start, event.end) for event in cleaned],
            [(0, 1_000), (1_400, 2_400)],
        )

    def test_retains_transition_run_totalling_exactly_threshold(self) -> None:
        subtitles = self.subtitles(
            (0, 1_000, "Hello\\N你好"),
            (1_000, 1_250, "你好"),
            (1_250, 1_500, "Goodbye\\N你好"),
            (1_500, 2_500, "Goodbye\\N再见"),
        )

        cleaned = remove_short_transition_runs(subtitles)

        self.assertEqual(len(cleaned), 4)

    def test_retains_standalone_short_cue(self) -> None:
        subtitles = self.subtitles(
            (0, 1_000, "Hello"),
            (1_000, 1_300, "Oh!"),
            (1_300, 2_300, "Goodbye"),
        )

        cleaned = remove_short_transition_runs(subtitles)

        self.assertEqual([event.text for event in cleaned], ["Hello", "Oh!", "Goodbye"])


if __name__ == "__main__":
    unittest.main()

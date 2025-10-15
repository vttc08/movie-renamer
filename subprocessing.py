from subtitle_filter import Subtitles as Subtitle
from pyasstosrt import Subtitle as ASSubtitle
from convertsub import utffix, convert_file
from tqdm import tqdm
import argparse
from pathlib import Path
from os import PathLike

"""
This is a one-shot script of subtitle processing that convert .ASS into .srt.
Then on all subtitles, remove SDH, fix UTF-8 and Simplified Chinese.
The script will run multiple actions and assume defaults for quick processing.
"""

def rmsdh(file: str|PathLike) -> None:
    """
    Remove SDH lines from .srt subtitles
    """
    subs = Subtitle(file)
    subs.filter()
    subs.save() # overwrite original file

def ass2srt(file: str|PathLike) -> None:
    """
    Convert .ass subtitle into .srt format
    """
    try:
        sub = ASSubtitle(file, remove_duplicates=True, removing_effects=True)
    except UnicodeDecodeError:
        utffix(file.name) # pyasstosrt cannot handle non UTF-8 files
        sub = ASSubtitle(file, remove_duplicates=True, removing_effects=True)
    sub.export(encoding='utf-8') # create a .srt file same name as the .ass

def process_one(file: str) -> None:
    """
    Convert .ass to .srt, then remove SDH and fixing Chinese simplified conversion for one subtitle file.
    """
    path = Path(file)
    if path.suffix not in ['.ass','.srt','.ssa']:
        return # preventing accidentally processing mkv file and causing OOM
    if path.suffix in ['.ass','.ssa']:
        # Convert ass to srt before next step
        ass2srt(path)
        path = path.with_suffix('.srt')
    rmsdh(path)
    convert_file(str(path))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs="+")
    args = parser.parse_args()
    for file in tqdm(args.file):
        process_one(file)
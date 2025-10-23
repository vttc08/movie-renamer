import opencc
import argparse
import chardet
import re
from tqdm import tqdm


# Create an OpenCC converter for Traditional to Simplified conversion
converter = opencc.OpenCC('t2s')

def utffix(file):
    '''Fix the encoding of the file to utf-8'''
    with open(file, 'rb') as f:
        content = f.read()
        detection = chardet.detect(content)
        encoding = detection['encoding']
    if encoding != 'utf-8':
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content.decode(encoding, errors='replace'))
        
def convert_chinese(text):
    """Convert Chinese text to Simplified Chinese using OpenCC"""
    # Check if the line contains Chinese characters
    if re.search('[\u4e00-\u9fa5]', text):
        text = converter.convert(text)
        # Remove any stray non-BMP characters that OpenCC may still produce
        return re.sub(r'[\U00010000-\U0010FFFF]', '', text)
    return text

def convert_file(file):
    if file.endswith('.srt'):
        utffix(file)
        with open(file, 'r', encoding='utf-8') as infile:
            lines = infile.readlines()
        with open(file, 'w', encoding='utf-8') as outfile:
            filename = file.split('/')[-1]
            for line in tqdm(lines, desc=f'Converting {filename}'):
                converted_line = convert_chinese(line.strip()) + '\n'
                outfile.write(converted_line)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs="+")
    args = parser.parse_args()
    for file in args.file:
        if file.endswith('.srt'):
            utffix(file)
            with open(file, 'r', encoding='utf-8') as infile:
                lines = infile.readlines()
            with open(file, 'w', encoding='utf-8') as outfile:
                filename = file.split('/')[-1]
                for line in tqdm(lines, desc=f'Converting {filename}'):
                    converted_line = convert_chinese(line.strip()) + '\n'
                    outfile.write(converted_line)
        else:
            pass
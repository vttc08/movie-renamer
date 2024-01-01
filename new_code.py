import os
import requests
import datetime
import xml.etree.ElementTree as ET
import ffmpeg
import time
import dotenv
import filedate

# this code assumes there are 2 versions of the movie in the destination folder with a nfo file with date added metadata, and the subtitles are added are for the HQ movie

dotenv.load_dotenv()
dir = input("Enter your directory.")
large_size = 0
small_size = float('inf')
larger_file = ''
smaller_file = ''
en_sub = ''
zh_sub = ''
mul_sub = ''

basename = os.path.basename(dir)
small_name = "更兼容的电影版本"

sub_zh = '中文字幕'
sub_mul = '双语中英文字幕'

os.chdir(dir)

def UHD(file):
    UHD_name = "4K-HDR 超高清蓝光电影"
    full = f'{basename} - {UHD_name}'
    new_name = f'{basename} - {UHD_name}.mkv'
    os.rename(file, new_name)
    sub_and_date(full, new_name)

def HD(file):
    HD_name = "BluRay - 1080p 蓝光电影" 
    full = f'{basename} - {HD_name}'
    new_name = f'{basename} - {HD_name}.mkv'
    os.rename(file, new_name)
    sub_and_date(full, new_name)


def sub_and_date(full, name):
    try:
        os.rename (mul_sub, f'{full}.zh.{sub_mul}.srt')
        os.rename (zh_sub, f'{full}.zh.{sub_zh}.srt')
        os.rename (en_sub, f'{full}.en.srt')
    except FileNotFoundError:
        print("One or more subtitle file is not found.")
    change_time(name, date)
    
def change_time(file, date):
    a_file = filedate.File(file)
    a_file.set(
        created = date,
        modified = date,
        accessed = date
    )


for file in os.listdir(dir):
    if file.endswith('.nfo'):
        with open(file, 'r', encoding='utf-8') as nfo:
            nfo_content = nfo.read()
            nfo_date = ET.fromstring(nfo_content).find('dateadded').text
            date = datetime.datetime.strptime(nfo_date, '%Y-%m-%d %H:%M:%S')
            dateadded = time.mktime(date.timetuple())
            nfo.close()
    if file.endswith('.mkv'):
        filestat = os.stat(file)
        size = filestat.st_size
        if size > large_size:
            large_size = size
            larger_file = file
        if size < small_size:
            small_size = size
            smaller_file = file
    if file.endswith('en.srt'):
        en_sub = file
    if file.endswith('zh.srt'):
        zh_sub = file
    if file.endswith('mul.srt'):
        mul_sub = file


os.rename(smaller_file, f'{basename} - {small_name}.mkv')
os.utime(f'{basename} - {small_name}.mkv', (dateadded,dateadded))
change_time(f'{basename} - {small_name}.mkv', date)

large_probe = ffmpeg.probe(larger_file)
resolution = int(large_probe['streams'][0]['width'])
if resolution > 1920:
    UHD(larger_file)
else:
    HD(larger_file)

url = f'{os.getenv("JF_URL")}/Library/Refresh?api_key={os.getenv("JF_API")}'
headers = {'accept': '*/*'}
response = requests.post(url, headers=headers)

print(response.status_code)  
# print(f'The larger file is {larger_file} and the smaller file is {smaller_file}')
            
            

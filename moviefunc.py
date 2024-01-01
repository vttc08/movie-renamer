import os
import requests
import datetime
import xml.etree.ElementTree as ET
import ffmpeg
import time
import dotenv
import filedate
import shutil
import threading
from colorama import Fore, Back, Style

# variables
dir = input("Enter your directory you want to rename or change date (enter scan to refresh JF server). ")

basename = os.path.basename(dir)

small_name = "更兼容的电影版本"
UHD_name = "4K-HDR 超高清蓝光电影"
HD_name = "BluRay - 1080p 蓝光电影" 

sub_list = ['en.srt','zh.srt','mul.srt']
renamed_subs = ['.en','.zh.中文简体字幕','.zh.双语中英文字幕']

dotenv.load_dotenv()
movie_dir = os.getenv('MOVIE_PATH')



def nfo_date():
    for file in os.listdir(dir):
        if file.endswith('.nfo'):
            with open(file, 'r', encoding='utf-8') as nfo:
                nfo_content = nfo.read()
                nfo_date = ET.fromstring(nfo_content).find('dateadded').text
                date = datetime.datetime.strptime(nfo_date, '%Y-%m-%d %H:%M:%S')
                dateadded = time.mktime(date.timetuple())
                
                nfo.close()
            return date

def size_detection():
    filesizes = []
    for file in os.listdir(dir):
        if file.endswith('.mkv'):
            size = os.stat(file).st_size
            filesizes.append((size, file))
            large_mkv_filesize = max(filesizes, key=lambda x: x[0])[0]
            large_mkv_file = [f[1] for f in filesizes if f[0] == large_mkv_filesize][0]
            small_mkv_filesize = min(filesizes, key=lambda x: x[0])[0]
            small_mkv_file = [f[1] for f in filesizes if f[0] == small_mkv_filesize][0]
    return large_mkv_file, small_mkv_file

def prober(large_mkv, small_mkv):
    large_mkv_file = ffmpeg.probe(large_mkv)
    resolution = int(large_mkv_file['streams'][0]['width'])
    os.rename(small_mkv, f'{basename} - {small_name}.mkv')
    if resolution > 1920:
        UHD(large_mkv)
    else:
        HD(large_mkv)

def UHD(file):
    new_name = f'{basename} - {UHD_name}.mkv'
    os.rename(file, new_name)

def HD(file):
    new_name = f'{basename} - {HD_name}.mkv'
    os.rename(file, new_name)

def sub(format):
    large_mkv, small_mkv = size_detection()
    name, ext = os.path.splitext(large_mkv)
    for item, language in zip (sub_list, renamed_subs):
        if format == 1:
            sub_format = f'{name}{language}.srt'
        if format == 2:
            sub_format = f'{name}{language}.srt'
            date = nfo_date()
            change_time(large_mkv, date)
            change_time(small_mkv, date)
        if os.path.exists(item):
            os.rename(item, sub_format)
    
def change_time(file, date):
    a_file = filedate.File(file)
    a_file.set(
        created = date,
        modified = date,
        accessed = date
    )

def refresh():
    dotenv.load_dotenv()
    url = f'{os.getenv("JF_URL")}/Library/Refresh?api_key={os.getenv("JF_API")}'
    headers = {'accept': '*/*'}
    response = requests.post(url, headers=headers)
    print(response.status_code)  

def ismoved(infile, outfile, start_time):
    try:
        filesize = os.path.getsize(infile)
    except FileNotFoundError:
        return False

    while True:
        if os.path.isfile(outfile):
            size = os.path.getsize(outfile) / (1024*1024*1024)
            current_time = time.time()
            elapsed_time = current_time - start_time
            return size, elapsed_time
        else:
            time.sleep(0.1)

def move(dir):
    # if the basename dir is not in the format "Text (Year)" then return error
    if not basename.endswith(")"):
        print("Folder name is not in the correct format")
        return

    # create a folder in the movie_dir with the same folder name as in dir
    if os.path.exists(movie_dir + basename):
        print("Folder already exists")
    else:
        os.mkdir(movie_dir + basename)
        print("Folder created")
        
        # Print the list of files in the directory for debugging
        print("Files in directory:", os.listdir(dir))
        
        # Loop through files in the directory
        for file in os.listdir(dir):
            if file.endswith('.srt'):
                print("Moving .srt file:", file)
                shutil.move(file, movie_dir + basename)

        for file in os.listdir(dir):
            start_time = time.time()
            try:
                filesize = os.path.getsize(file) / (1024*1024*1024)
            except FileNotFoundError:
                continue
            
            thread = threading.Thread(target=shutil.move, args=(file, movie_dir + basename))
            thread.start()

            while thread.is_alive():
                try:
                    size_gb, elapsed_time = ismoved(file, movie_dir + basename + "\\" + file, start_time)
                    print(f"{file}: {Fore.LIGHTRED_EX}{size_gb:.2f}{Style.RESET_ALL} GB of {Fore.LIGHTBLUE_EX}{filesize:.2f}{Style.RESET_ALL} GB | {Fore.GREEN}{size_gb/filesize*100:.4f}{Style.RESET_ALL} %   | Average speed is {Fore.CYAN}{size_gb/elapsed_time*1024:.2f}{Style.RESET_ALL} MB/s")
                    time.sleep(0.8)
                except:
                    pass

        # change to this program dir and remove the original dir
        os.chdir("..")
        os.rmdir(dir)


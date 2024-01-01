from moviefunc import *


os.chdir(dir)

if __name__ == '__main__':
    date = nfo_date()
    for f in os.listdir(dir):
        if f.endswith(".mkv"):
            change_time(f, date)
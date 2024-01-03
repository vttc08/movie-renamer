from moviefunc import *
import glob

def onemkv():
    sub(1)

def twomkv():
    large_mkv, small_mkv = size_detection()
    prober(large_mkv, small_mkv)
    sub(2)


if __name__ == "__main__":
    if dir.startswith("/mnt/config"):
        refresh()
    else:
        os.chdir(dir)
        mkvcounter = len(glob.glob1(dir,"*.mkv"))
        if mkvcounter > 1:
            twomkv()
        if mkvcounter == 1:
            onemkv()
        move(dir)

    
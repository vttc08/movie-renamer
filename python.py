import filedate
from new_code import *




a = 'M:/film.mkv'
a_file = filedate.File(a)
 
a_file.set(
    created = "2022-01-05",
    modified = "2022-01-05",
    accessed = "2022-01-05"
)
 
after = filedate.File(a)
print(after.get())
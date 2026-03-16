import shutil
import os

# создаем папку
os.mkdir("folder")

# создаем файл
with open("file.txt", "w") as f:
    f.write("Hello")

# перемещаем файл
shutil.move("file.txt", "folder/file.txt")

print("File moved")
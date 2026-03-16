import os

# текущая папка
print("Current directory:", os.getcwd())

# создать папку
os.mkdir("test_folder")

# список файлов
print("Files:", os.listdir())

# перейти в папку
os.chdir("test_folder")
print("Now in:", os.getcwd())

# вернуться назад
os.chdir("..")

# удалить папку
os.rmdir("test_folder")
import os

#1
# os.remove("demofile.txt")

#2
if os.path.exists("demofile.txt"):
  os.remove("demofile.txt")
else:
  print("The file does not exist")
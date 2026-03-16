#1
f = open("demofile.txt")
print(f.read())

#2
# f = open("D:\\myfiles\welcome.txt")
# print(f.read())

#3
with open("demofile.txt") as f:
  print(f.read())

#4
f = open("demofile.txt")
print(f.readline())
f.close()

#5
with open("demofile.txt") as f:
  for x in f:
    print(x)
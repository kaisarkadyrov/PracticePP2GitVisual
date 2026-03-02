#1
import re

txt = "The rain in Spain"
x = re.search("^The.*Spain$", txt)

print(x)

#2

txt = "The rain in Spain"
x = re.findall("Portugal", txt)
print(x)

#3

txt = "The rain in Spain"
x = re.search("\s", txt)

print("The first white-space character is located in position:", x.start())

#4
txt = "The rain in Spain"
x = re.split("\s", txt)
print(x)

#5
txt = "The rain in Spain"
x = re.sub("\s", "9", txt)
print(x)


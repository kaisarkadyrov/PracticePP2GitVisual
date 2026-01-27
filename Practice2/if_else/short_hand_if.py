#1 One-liner if statement
a = 5
b = 2
if a > b: print("a is greater than b")

#2 Assignning value
a = 10
b = 20
bigger = a if a > b else b
print("Bigger is", bigger)

#3
a = 330
b = 330
print("A") if a > b else print("=") if a == b else print("B")

#4
username = ""
display_name = username if username else "Guest"
print("Welcome,", display_name)

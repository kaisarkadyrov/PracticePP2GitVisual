#1
x = 5
y = "John"
print(x)
print(y)

#2
x = str(3)  
y = int(3)   
z = float(3)  
print(x, y, z)

#3
x, y, z = "Orange", "Banana", "Cherry"
print(x)
print(y)
print(z)

#4
x = "Python "
y = "is "
z = "awesome"
print(x + y + z)

#5
x = "awesome"

def myfunc():
  x = "fantastic"
  print("Python is " + x)

myfunc()

print("Python is " + x)
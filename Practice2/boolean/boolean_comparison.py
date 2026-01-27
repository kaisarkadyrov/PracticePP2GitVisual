#1
x = 5
y = 3

print(x == y)
print(x != y)
print(x > y)
print(x < y)
print(x >= y)
print(x <= y)

#2 Chaining Comparison Operators
x = 5

print(1 < x < 10)

print(1 < x and x < 10)

#3
x = ["apple", "banana"]
y = ["apple", "banana"]
z = x

print(x is z)
print(x is y)
print(x == y)

#4
fruits = ["apple", "banana", "cherry"]

print("banana" in fruits)
#1
words = ["apple", "banana", "cherry"]

for i, word in enumerate(words, start=1):
    print(i, word)

#2
names = ["Alice", "Bob", "Charlie"]
scores = [90, 85, 88]

for name, score in zip(names, scores):
    print(name, score)

#3
names = ["Alice", "Bob"]
ages = [20, 25]
cities = ["Paris", "London"]

for n, a, c in zip(names, ages, cities):
    print(n, a, c)
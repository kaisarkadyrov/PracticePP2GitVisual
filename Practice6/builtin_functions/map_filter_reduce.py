#1
numbers = [1, 2, 3, 4]

result = list(map(lambda x: x**2, numbers))

print(result)

#2
words = ["cat", "elephant", "hi"]

lengths = list(map(len, words))

print(lengths)

#3
words = ["cat", "elephant", "hi"]

lengths = list(map(len, words))

print(lengths)

#4
numbers = [1, 2, 3, 4, 5, 6]

evens = list(filter(lambda x: x % 2 == 0, numbers))

print(evens)

#5
from functools import reduce

numbers = [7, 3, 10, 2, 8]

maximum = reduce(lambda a, b: a if a > b else b, numbers)

print(maximum)
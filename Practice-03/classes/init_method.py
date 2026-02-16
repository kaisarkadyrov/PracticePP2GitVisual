#1
class Person:
  def __init__(self, name, age):
    self.name = name
    self.age = age

p1 = Person("Emil", 36)

print(p1.name)
print(p1.age)

#2
class Person2:
  def __init__(self, name, age=18):
    self.name = name
    self.age = age

p2 = Person2("Emil")
p3 = Person2("Tobias", 25)

print(p2.name, p2.age)
print(p3.name, p3.age)
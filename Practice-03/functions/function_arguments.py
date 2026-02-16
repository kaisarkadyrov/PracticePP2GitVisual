#1
def my_function(fname):
  print(fname + " Refsnes")

my_function("Emil")
my_function("Tobias")
my_function("Linus")

#2
def my_function(name):
  print("Hello", name)

my_function("Emil")

#3
def my_function(fname, lname):
  print(fname + " " + lname)

my_function("Emil", "Refsnes")

#4
def my_function(country = "Norway"):
  print("I am from", country)

my_function("Sweden")
my_function("India")
my_function()
my_function("Brazil")
import datetime
#1

x = datetime.datetime.now()
print(x)

#2
y = datetime.datetime.now()

print(y.year)
print(y.strftime("%A"))

#3
z = datetime.datetime(2020, 5, 17)

print(z)


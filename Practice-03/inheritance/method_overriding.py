class Person:
    def __init__(self, fname, lname):
        self.firstname = fname
        self.lastname = lname

    def printinfo(self):
        print(f"Person: {self.firstname} {self.lastname}")


class Student(Person):
    def __init__(self, fname, lname, year):
        super().__init__(fname, lname)
        self.graduationyear = year

    # Method Overriding
    def printinfo(self):
        print(f"Student: {self.firstname} {self.lastname}, Graduation year: {self.graduationyear}")


p = Person("Alice", "Brown")
s = Student("John", "Doe", 2026)

p.printinfo()
s.printinfo()

class Person:
    def __init__(self, fname, lname):
        self.firstname = fname
        self.lastname = lname

    def printname(self):
        print(f"Name: {self.firstname} {self.lastname}")


class Student(Person):
    def __init__(self, fname, lname, year):
        super().__init__(fname, lname) 
        self.graduationyear = year     

    def printstudent(self):
        print(f"Name: {self.firstname} {self.lastname}, Graduation year: {self.graduationyear}")


x = Student("John", "Doe", 2026)

x.printname()

x.printstudent()

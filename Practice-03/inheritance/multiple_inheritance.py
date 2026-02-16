class Person:
    def __init__(self, name):
        self.name = name

    def show_person(self):
        print(f"Name: {self.name}")


class Worker:
    def __init__(self, salary):
        self.salary = salary

    def show_salary(self):
        print(f"Salary: {self.salary}")


class StudentWorker(Person, Worker):
    def __init__(self, name, salary, university):
 
        Person.__init__(self, name)
        Worker.__init__(self, salary)

        self.university = university

    def show_all(self):
        print(f"Name: {self.name}")
        print(f"Salary: {self.salary}")
        print(f"University: {self.university}")


x = StudentWorker("John", 2000, "MIT")

x.show_person()
x.show_salary()
x.show_all()

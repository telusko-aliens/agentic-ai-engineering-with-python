name = 'Akshay'
age: int = 'Thirty'

#print(name)
#print(age)

def add_student(name: str, age: int):
    return {
        'name': name,
        'age': age
    }

student = add_student(10, 'Ten')
print(student)


class Student:
    def __init__(self, name, age, email):
       self.name = name
       self.age = age
       self.email = email

# Data Type Validation
# Value Validation

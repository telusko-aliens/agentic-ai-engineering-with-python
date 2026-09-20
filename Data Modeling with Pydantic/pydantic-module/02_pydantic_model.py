from pydantic import BaseModel, StrictInt, StrictBool

class Student(BaseModel):
    name: str
    age: StrictInt
    is_enrolled: StrictBool

student = Student(name='Tom', age=20, is_enrolled=True)
print(student.name)
print(student.age)
print(student.is_enrolled)

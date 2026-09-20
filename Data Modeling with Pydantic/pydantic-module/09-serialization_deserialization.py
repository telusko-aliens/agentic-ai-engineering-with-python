from pydantic import BaseModel, Field
from datetime import date


class Student(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    age: int = Field(gt=0, lt=120)
    email: str
    enrolled_date: date = date.today()

studen1 = Student(
    name='Akshay',
    age=30,
    email='akshay@telusko.com'
)

print(type(studen1))
print(studen1.model_dump()) #model -> dict
print(studen1.model_dump(mode='json')) #model -> json
print(studen1.model_dump_json()) #model -> json

#include
print(studen1.model_dump(include={'name', 'email'}))
print(studen1.model_dump_json(include={'name', 'email'}))

#exclude
print(studen1.model_dump(exclude={'name', 'email'}))
print(studen1.model_dump_json(exclude={'name', 'email'}))

student_json_api = {'name': 'Aman', 'age': 28, 'email': 'aman@test.com', 'enrolled_date': '2026-02-01'}
student2 = Student.model_validate(student_json_api)
print(student2)

json_from_api = '{"name": "Harsh", "age": 25, "email": "harsh@example.com", "signup_date": "2026-03-10"}'
student3 = Student.model_validate_json(json_from_api)
print(type(student3))
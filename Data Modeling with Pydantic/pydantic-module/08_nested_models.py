from pydantic import BaseModel, Field

class Course(BaseModel):
    title: str
    duration_in_hours: int
    price: float = Field(gt=0)

class Student(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    age: int = Field(gt=0, lt=120)
    email: str
    courses: list[Course]

course1 = Course(title='Pydantic', duration_in_hours=3, price=19.99)
course2 = Course(title='Advanced Python', duration_in_hours=5, price=29.99)

student1 = Student(
    name='Akshay',
    age=30,
    email='akshay@telusko.com',
    courses=[course1, course2]
)

print(student1)

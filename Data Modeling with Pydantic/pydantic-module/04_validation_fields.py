from pydantic import BaseModel, StrictInt, StrictBool, ConfigDict, Field, EmailStr
from typing import Optional
from pydantic_extra_types.phone_numbers import PhoneNumber

class Student(BaseModel):
    model_config = ConfigDict(validate_default=True)

    name: str | None = Field(
        default=None,
        description='This is name of the student',
        min_length=2,
        max_length=50
    )
    age: StrictInt = Field(
        default=None,
        gt=18,
        lt=50
    )
    is_enrolled: Optional[StrictBool] = True
    #email: str | None = Field(pattern=r'^\S+@\S+\.\S+$',description='This is the student email')
    email: EmailStr
    phone_number: PhoneNumber

student = Student(age=35, name='Akshay', email='akshay@telusko.com', phone_number='+919887987988')
print(student.name)
print(student.age)
print(student.is_enrolled)
print(student.email)
print(student.phone_number)
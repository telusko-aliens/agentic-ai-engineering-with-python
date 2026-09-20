from pydantic import BaseModel, StrictInt, StrictBool, ConfigDict
from typing import Optional

class Student(BaseModel):
    model_config = ConfigDict(validate_default=True)

    name: str | None = 'NA'
    age: StrictInt = None
    is_enrolled: Optional[StrictBool] = True
    email: str | None = None

student = Student(age=20)
print(student.name)
print(student.age)
print(student.is_enrolled)
print(student.email)
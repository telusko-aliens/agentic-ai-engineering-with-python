from pydantic import BaseModel, ConfigDict, Field, computed_field


class Student(BaseModel):
    model_config = ConfigDict(validate_default=True)

    name: str = Field(min_length=2, max_length=50)
    email: str

    @computed_field
    @property
    def username(self) -> str:
        return self.email.split('@')[0]

student1 = Student(name='Akshay', email='akshayagarwal@telusko.com')
print(student1)

student1.email = 'something@telusko.com'
print(student1)
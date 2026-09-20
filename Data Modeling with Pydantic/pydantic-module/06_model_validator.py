from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator


class Student(BaseModel):
    model_config = ConfigDict(validate_default=True)

    name: str = Field(min_length=2, max_length=50)
    password: str
    confirm_password: str

    @model_validator(mode='before')
    @classmethod
    def validate_strings(cls, data):
        print('Before called')
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    data[key] = value.strip()
        return data

    @model_validator(mode='after')
    def validate_passwords(self):
        print('After called')
        if self.password != self.confirm_password:
            raise ValueError('password and confirm password should be same')
        return self

    @model_validator(mode='wrap')
    @classmethod
    def log_validations(cls, data, handler):
        print(f'raw data: {data}')
        student = handler(data)
        print(f'student name: {student.name}')
        return student


student1 = Student(name='  Akshay  ',password='secret123   ',confirm_password='secret123',
)

print(student1)
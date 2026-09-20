from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator

class Student(BaseModel):
    model_config = ConfigDict(validate_default=True)

    name: str = Field(min_length=2, max_length=50)
    age: int
    email: EmailStr
    phone_no: str | None = None

    @field_validator('name', mode='after')
    @classmethod
    def clean_name(cls, name):
        if any(ch.isdigit() for ch in name):
            raise ValueError('name must not contain digits')
        return name
    
    @field_validator('phone_no', mode='before')
    @classmethod
    def format_phone_number(cls, phone_no):
        if isinstance(phone_no, str):
            return phone_no.replace('-', '').replace(' ', '').replace('+', '')
        return phone_no

    @field_validator('email', mode='wrap')
    @classmethod
    def validate_email_domains(cls, email, handler):
        email = email.strip().lower()
        validated_email = handler(email)
        blocked_domains = {'example.org', 'test.com'}
        domain = validated_email.split('@')[-1]
        if domain in blocked_domains:
            raise ValueError(f'emails from "{domain}" are not allowed')
        return validated_email

    @field_validator('age', mode='plain')
    @classmethod
    def validate_age(cls, age):
        if not isinstance(age, int):
            raise ValueError('age must be an int')
        if not (18 < age < 50):
            raise ValueError('age must be between 18 to 50')
        return age

student = Student(age='Ten', name='Akshay', email='akshay@telusko.com', phone_no='+9198899-87678')
print(student.name)
print(student.age)
print(student.email)
print(student.phone_no)
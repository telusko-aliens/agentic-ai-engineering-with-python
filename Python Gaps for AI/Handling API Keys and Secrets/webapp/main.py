import os
from dotenv import load_dotenv

load_dotenv()

def main():
    print('Welcome to Telusko')

    USER_NAME = os.getenv('USER_NAME')
    print(USER_NAME)

    API_KEY = os.getenv('API_KEY')
    print(API_KEY)

    ADDRESS = os.getenv('ADDRESS')
    print(ADDRESS)

    USER_EMAIL = os.getenv('USER_EMAIL')
    print(USER_EMAIL)


if __name__ == "__main__":
    main()

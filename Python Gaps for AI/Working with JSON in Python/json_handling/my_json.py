import json

# this is json, not python
# we can only use double quotes
# handle this carefully, no trailing commas
user_json = '''
{
    "name": "Akshay",
    "bio": "Hello 🙏, We are learning JSON in Python",
    "experience": 10,
    "is_member": true,
    "balance": null
}
'''

def main():

    # Reading the Json From String
    user_data = json.loads(user_json)
    print(user_data)
    print(type(user_data))

    # Updating Json
    user_data['balance'] = 200

    # update another field - invalid
    #biodata = user_data['biodata']
    
    # error, no biodata field is present
    # don't use like this
    biodata = user_data.get('biodata', 'Value not found')
    print(biodata)

    # Adding a field in JSON
    user_data['skills'] = ["python", "sql"]
    
    # Adding values to field
    #user_data.get('skills').append('Java')
    print(user_data)

    #Removing values from json
    del user_data['skills'][0]
    print(user_data)

    #Removing the entire field from json
    del user_data['skills']
    print(user_data)

    #Nested Object
    skills = [{
        'subject': 'Java',
        'experience': 2
    },
    {
        'subject': 'Python',
        'experience': 3
    }]

    user_data['skills'] = skills

    # handling the field updates
    if user_data.get('skills')[0].get('experence') != None:
        user_data['skills'][0]['experence'] = 4
    else:
        print('No such field found!')

    print(user_data)

    #once we are done we need to update the json
    # Updating String again from json
    # show indent - 2,4
    # show ascii code for icon
    updated_user_json = json.dumps(user_data, indent=2, ensure_ascii=False)
    print(updated_user_json)

    #NOW can can do everything using file as well

    with open('students.json', 'r') as file:
        user_data = json.load(file)
        print(user_data)

    user_data['students'][0]['name'] = 'Shramik'

    print(user_data)

    # while udpating the json, show indent, ensure_ascii again
    with open('students.json', 'w') as file:
        json.dump(user_data, file, indent=2, ensure_ascii=False)
    
if __name__ == "__main__":
    main()

from time import sleep as tsleep

def store_user_data(first_name,last_name,email,gender,phone_number):
    print("From thread, hello")
    tsleep(4)
    stringy = """Creating user {} {}
    email: {}
    gender: {}
    phone_number: {}
    """.format(first_name,last_name,email,gender,phone_number)
    print(stringy)

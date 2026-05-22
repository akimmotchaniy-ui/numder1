from texts import *

name = input(MSG_INPUT_NAME).strip()

if name.replace(" ", "").isalpha():
    name = name.title()
    print(MSG_NAME_OK.format(name))

age = input(MSG_INPUT_AGE).strip().lstrip("0")

if age.isdigit():
    print(MSG_AGE_OK.format(age))

phone = input(MSG_INPUT_PHONE).strip()

if phone.isdigit():
    print(MSG_PHONE_OK.format(phone))

print(MSG_FINISH)
from pymongo import MongoClient
from dotenv import load_dotenv, find_dotenv
import os
import pprint

# find env file
load_dotenv(find_dotenv())

# connect to MongoDb database
CONNECTION_STRING = os.environ.get("mongo_URI")
client = MongoClient(CONNECTION_STRING)

# connect to relavent collections
db = client.AttendaceDB
groups = db.groups
accounts = db.accounts
attendance = db.attendance
account_group = db.account_group

# Walks users the account creation on entry
def create_account():
    username = input("\nPlease enter an account username: ")
    existing_user = accounts.find_one({"username": username})

    # If username is not in use, user will creat account under their selected username
    if not existing_user:
        password = input("Please enter an account password: ")
        first_name = input("What is your first name? ")
        last_name = input("What is your last name? ")

        document = {
            "username":username,
            "password":password,
            "first_name":first_name,
            "last_name":last_name
        }

        # registering account in account database
        insert_document(accounts, document)
        new_account_doc = accounts.find_one({"username": username}, {"username": 1, "password": 1, "first_name":1, "last_name":1})

        return new_account_doc
    # User must choose another username
    else:
        print("Username currently in use, please choose another")
        return


# will insert any given document to any given collection
def insert_document(collection, document):
    inserted_id = collection.insert_one(document).inserted_id
    return inserted_id


# Will check if a user can log in with the given credentials
def login():
    username = input("\nPlease input your account username: ")
    password = input("Please enter your account password: ")

    account = accounts.find_one({"username": username, "password": password}, {
        "username": 1, "password": 1, "first_name":1, "last_name":1})

    if account:
        return account
    else:
        return

# Will present the user a navigation page based off of their groups
def user_options_menu(user_doc):
    print("""\nWhat page would you like to navigate to? 
    1. Account options
    2. Create new group
    3. Join group""")

    concurrent_groups = account_group.find({"user_id": user_doc["_id"]}, {"group_id":1})

    if concurrent_groups:

        iterator = 4

        for group in concurrent_groups:
            group_doc = groups.find_one({"_id":group["group_id"]}, {"group_name":1})
            print("    {}. {}".format(iterator, group_doc["group_name"]))
            iterator+=1

    nav_key = int(input())

    return nav_key

def create_group(user_doc):
    group_name = input("\nWhat would you like to name your group? ")
    existing_group = groups.find_one({"group_name": group_name})

    # If group name is not in use, user will create group under their selected group name
    if not existing_group:
        join_code = input("What would you like to set the join code to? ")

        group_doc = {
            "group_name": group_name,
            "join_code": join_code
        }

        # registering group in group database
        insert_id = insert_document(groups, group_doc)

        composite_doc = {
            "group_id": insert_id,
            "user_id": user_doc["_id"],
            "user_role": "Admin"
        }

        insert_document(account_group, composite_doc)


    # User must choose another group name
    else:
        print("Group name currently in use, please choose another")
        return

def join_group(user_doc,group_name,join_code):

    group = groups.find_one({"group_name":group_name, "join_code":join_code})

    if group:

        composite_doc = {
            "group_id": group["_id"],
            "user_id": user_doc["_id"],
            "user_role": "Member"
        }

        insert_document(account_group, composite_doc)

    else:
        print("Not a valid group and/or join code")

def account_tools(user_doc):
    print("welcome to account tools!")
    print(f"""Your options are:
    1. first name: {user_doc["first_name"]}
    2. last name: {user_doc["last_name"]}
    3. username: {user_doc["username"]}
    4. password: {user_doc["password"]}
    5. delete account""")
    nav_choice = int(input())

    if nav_choice == 1:
        new_name = input("\nWhat would you like to change your first name to? ")
        update_doc_key(user_doc, "first_name", new_name)

    if nav_choice == 2:
        new_name = input("\nWhat would you like to change your last name to? ")
        update_doc_key(user_doc, "last_name", new_name)

    if nav_choice == 3:
        new_user = input("\nWhat would you like to change your username to? ")
        new_username = accounts.find_one({"username":new_user})

        if not new_username:
            update_doc_key(user_doc, "last_name", new_name)

        else:
            print("Username is already taken.")
    
    if nav_choice == 4:
        new_pass = input("\nWhat would you like to change your password to? ")
        update_doc_key(user_doc, "password", new_pass)

    if nav_choice == 5:
        print("\nPlease enter your username and password to delete your account")
        username = input("Username: ")
        password = input("Password: ")

        account = accounts.find_one({"username":username, "password":password})
        
        if account:
            accounts.delete_one({"_id":account["_id"]})

            concurrent_groups = account_group.find({"user_id": user_doc["_id"]}, {"group_id":1, "user_role":1})

            if concurrent_groups:
                for document in concurrent_groups:
                    account_group.delete_one({"_id":document["_id"]})

                    if document["user_role"] == "Admin":
                        groups.delete_one({"_id":document["group_id"]})
                        member_group = account_group.find({"group_id":document["group_id"]})

                        if member_group:
                            for member in member_group:
                                account_group.delete_one({"_id":member["_id"]})

        else:
            print("incorrect username or password")

def update_doc_key(document, key, value):
    _id = document["_id"]

    updates = {
        "$set": {key: document[key]}
    }

    attendance.update_one({"_id":_id}, updates)

if __name__ == "__main__":

    # present user with entry options
    print("""Welcome to AttendanceDB!
Would you like to do:
    1. log in to existing account
    2. Create an AttendanceDB account""")
    
    entry_option = int(input())

    # Runs user through entry process
    if entry_option == 1:
        user_doc = login()
    if entry_option == 2:
        user_doc = create_account()

    # Provides options if user logged in
    if user_doc is None:
        print("Unsuccessful log in")
    else:
        nav_menu = user_options_menu(user_doc)

    # Expanding nav menu options
    if nav_menu == 1:
        account_tools(user_doc)
    if nav_menu == 2:
        create_group(user_doc)
    if nav_menu == 3:
        group_name = input("\nWhat group would you like to join? ")
        join_code = input("Please input the groups join_code: ")
        join_group(user_doc, group_name, join_code)

    


from pymongo import MongoClient
from dotenv import load_dotenv, find_dotenv
import os
import datetime

# find env file
load_dotenv(find_dotenv())

# connect to MongoDb database
CONNECTION_STRING = os.environ.get("mongo_URI")
client = MongoClient(CONNECTION_STRING)

# connect to relavent collections
DB = client.AttendaceDB
GROUPS = DB.groups
ACCOUNTS = DB.accounts
ATTENDANCE = DB.attendance
ACCOUNT_GROUP = DB.account_group

# Walks users the account creation on entry
def create_account():
    username = input("\nPlease enter an account username: ")
    existing_user = ACCOUNTS.find_one({"username": username})

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
        insert_document(ACCOUNTS, document)
        new_account_doc = ACCOUNTS.find_one({"username": username}, {"username": 1, "password": 1, "first_name":1, "last_name":1})

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

    account = ACCOUNTS.find_one({"username": username, "password": password}, {
        "username": 1, "password": 1, "first_name":1, "last_name":1})

    if account:
        return account
    else:
        return

# Will present the user a navigation page based off of their groups
def user_options_menu(user_groups):
    print("""\nWhat page would you like to navigate to? 
    1. Account options
    2. Create new group
    3. Join group""")

    # provides user interface so that user can interact with their groups
    iterator = 4

    for name in user_groups:
        print(f"    {iterator}. {name}")
        iterator+=1

    nav_key = int(input())

    return nav_key

# creates a group
def create_group(user_doc, group_name, join_code):
    existing_group = GROUPS.find_one({"group_name": group_name})

    # If group name is not in use, user will create group under their selected group name
    if not existing_group:

        group_doc = {
            "group_name": group_name,
            "join_code": join_code
        }

        # registering group in group database
        insert_id = insert_document(GROUPS, group_doc)

        composite_doc = {
            "group_id": insert_id,
            "user_id": user_doc["_id"],
            "user_role": "Admin"
        }

        insert_document(ACCOUNT_GROUP, composite_doc)


    # User must choose another group name
    else:
        print("Group name currently in use, please choose another")
        return

# allows user to join a group
def join_group(user_doc,group_name,join_code, user_groups):

    # looks for groups best off user provided credentials
    group = GROUPS.find_one({"group_name":group_name, "join_code":join_code})

    # if user provided proper credentials they will be added to the group
    if group:

        # looks to see if user already joined group
        if group_name not in user_groups:
            composite_doc = {
                "group_id": group["_id"],
                "user_id": user_doc["_id"],
                "user_role": "Member"
            }

            insert_document(ACCOUNT_GROUP, composite_doc)

        else:
            print("Already joined group")

    else:
        print("Not a valid group and/or join code")

# provides the user with account tools interface
def account_tools(user_doc):

    # Options for user to choose from
    print("welcome to account tools!")
    print(f"""Your options are:
    1. first name: {user_doc["first_name"]}
    2. last name: {user_doc["last_name"]}
    3. username: {user_doc["username"]}
    4. password: {user_doc["password"]}
    5. delete account""")
    nav_choice = int(input())

    # if user chooses to change first name
    if nav_choice == 1:
        new_name = input("\nWhat would you like to change your first name to? ")
        update_doc_key(user_doc, "first_name", new_name)

    # if user chooses to change last name
    if nav_choice == 2:
        new_name = input("\nWhat would you like to change your last name to? ")
        update_doc_key(user_doc, "last_name", new_name)

    # if user chooses to change username
    if nav_choice == 3:
        new_user = input("\nWhat would you like to change your username to? ")
        
        # check that the chosen username is not already in use before being changed
        new_username = ACCOUNTS.find_one({"username":new_user})
        if not new_username:
            update_doc_key(user_doc, "last_name", new_name)

        else:
            print("Username is already taken.")
    
    # if user chooses to change password
    if nav_choice == 4:
        new_pass = input("\nWhat would you like to change your password to? ")
        update_doc_key(user_doc, "password", new_pass)

    # if user chooses to delete account
    if nav_choice == 5:
        print("\nPlease enter your username and password to delete your account")
        # verification before account deletion
        username = input("Username: ")
        password = input("Password: ")

        # confirms account verification
        account = ACCOUNTS.find_one({"username":username, "password":password})
        

        if account:

            # deletes account
            ACCOUNTS.delete_one({"_id":account["_id"]})

            # finds all groups that user is concurrently enrolled in
            concurrent_groups = ACCOUNT_GROUP.find({"user_id": user_doc["_id"]}, {"group_id":1, "user_role":1})

            if concurrent_groups:
                for document in concurrent_groups:
                    # deletes membership record in group
                    ACCOUNT_GROUP.delete_one({"_id":document["_id"]})

                    # logic for if user is admin of a group but deleting an account
                    # decided that if user deletes their account all groups they are admin of will also be deleted
                    # This prevents any stray groups in the database being left without an admin
                    # in the future I would like to avoid deleting entire groups but either promoting someone to admin 
                    # or allowing other group admins to keep the group running. n^2 is not desirable either.
                    # implement delete_group function
                    if document["user_role"] == "Admin":
                        GROUPS.delete_one({"_id":document["group_id"]})
                        member_group = ACCOUNT_GROUP.find({"group_id":document["group_id"]})

                        # deletes the documents of other members being a part of the now deleted group
                        if member_group:
                            for member in member_group:
                                ACCOUNT_GROUP.delete_one({"_id":member["_id"]})

        else:
            print("incorrect username or password")

# simple function for changing a document value
def update_doc_key(document, key):
    _id = document["_id"]

    updates = {
        "$set": {key: document[key]}
    }

    ATTENDANCE.update_one({"_id":_id}, updates)

# Finds and creates a list of all groups that user is currently a part of
def find_user_groups(user_doc):
    user_groups = ACCOUNT_GROUP.find({"user_id":user_doc["_id"]}, {"group_id":1, "user_role":1})

    if user_groups:
        return user_groups

# grabs the names of group documents provided to it        
def fetch_group_names(group_docs):
    names = []

    if group_docs:
        for document in group_docs:
            name_doc = GROUPS.find_one({"_id": document["group_id"]}, {"group_name":1})
            name = name_doc["group_name"]
            names.append(name)

    return names

# checks if a user is a group admin or not
def check_admin(group_name, user_doc):
    group_doc = GROUPS.find_one({"group_name": group_name})

    if group_doc:

        account_group_doc = ACCOUNT_GROUP.find_one({"user_id":user_doc["_id"], "group_id": group_doc["_id"]}, {"user_role":1})

        if account_group_doc["user_role"] == "Admin":
            return True
        else:
            return False

# will insert an attendance marker for the day
def mark_attendance(user_doc, group_name):
    today = datetime.date.today()

    doc = {
        "group_name": group_name,
        "date": str(today),
        "first_name": user_doc["first_name"],
        "last_name": user_doc["last_name"]
    }

    insert_document(ATTENDANCE, doc)

# provides UI for the admin to control some group features
def admin_group_control(nav_menu, group_name):
    if nav_menu == 1:
        today = str(datetime.date.today())

        marked_attendance = ATTENDANCE.find({"group_name": group_name, "date":today}, {"first_name":1, "last_name":1})

        print(f'\nThe people who marked attendace for today were: ')
        for mark in marked_attendance:
            print(f"{mark['first_name']} {mark['last_name']}")

    if nav_menu == 2:
        print("\nTo verify, please provide the following information: ")
        username = input("Username: ")
        password = input("Password: ")

        user = ACCOUNTS.find_one({"username": username, "password":password})
        if user: 
            delete_group(group_name)
            print("Your group has been successfully deleted.")

# allows for the deletion of a group
def delete_group(group_name):
    group_doc = GROUPS.find_one({"group_name":group_name})

    GROUPS.delete_one({"_id": group_doc["_id"]})

    ACCOUNT_GROUP.delete_many({"group_id": group_doc["_id"]})

    ATTENDANCE.delete_many({"group_name": group_name})


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

    user_groups = find_user_groups(user_doc)
    group_names = fetch_group_names(user_groups)

    # Provides options if user logged in
    if user_doc is None:
        print("Unsuccessful log in")
    else:
        nav_menu = user_options_menu(group_names)

    # Expanding nav menu options
    if nav_menu == 1:
        # account tools option
        account_tools(user_doc)
    if nav_menu == 2:
        # creating group options
        group_name = input("\nWhat would you like to name your group? ")
        join_code = input("What would you like to set the join code to? ")
        create_group(user_doc, group_name, join_code)

    if nav_menu == 3:
        # joining group options
        group_name = input("\nWhat group would you like to join? ")
        join_code = input("Please input the groups join_code: ")
        join_group(user_doc, group_name, join_code, user_groups)

    if nav_menu > 3:
        # group contol options
        group_choice = group_names[nav_menu-4]
        admin = check_admin(group_choice, user_doc)

        # check to see if the UI presented is admin interface
        if admin:
            print("""\nWould you like to
    1. Get attendance report for the day
    2. Delete group""")
            admin_choice = int(input(""))
            admin_group_control(admin_choice, group_choice)
        
        # check to see if the UI presented is member interface
        else:
            attendance_choice = input("\nWould you like to mark attendance for the day?(y/n) ")
            
            if attendance_choice == "y":
                mark_attendance(user_doc, group_choice)
                print("You have successfully marked your attendance for today.")





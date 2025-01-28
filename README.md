# Attendance-DB Overview

This software is at its core an attendance software. Users should be able to mark themselves present within this software's UI and then the admin of whatever group they are in should be able to auto-generate a report of who was present during the day the generate the report. This report is queried from the cloud database collections that contain the reported attendance. While these are the features at the core of the software, there is plenty of additional feautures to help users. These features include: user authentication, account flexibilty, taking part in multiple groups, and many more. The features provided could definitely be improved upon, however, I do believe they offer a good baseline for quality interface and database interactment. To use this software, the script simply needs to be ran, then a user should be able to interact with it to do all their desired operations.

I wrote this software intending to simply learn how to use cloud databases within the software I write. However, while developing out this project I expanded this goal to to trying to create software that is quality and has potential for being more than just a terminal script. At the moment I would not classify this software as having met that goal, but I would say it is working towards it.

Below is a video link to a demonstration of the software. In the link an error occurs where the program cannot overwrite past data. Since then that bug has been it fixed. The software was originaly trying to overwrite documents in the incorrect collection which resulted in the error observed.

[Software Demo Video](https://youtu.be/bI6N4RyoNV)

# Cloud Database

For this project I made use of the MongoDB Atlas databases.

The database itself consists of 4 collections. The collections are as follows: groups, accounts, group-accounts, and attendance. The group collection consists of data about the groups that members and admins can take part in and use, the accounts are all users currently registered with the database, group-accounts is the composite collection between the last two mentioned collections which allows for ease of querying when it comes to group membership questions, and the attendance collection is where all marked attendace documents will be stored.

# Development Environment
I developed this software within Visual Studio Code.

To develop this software Python and the packages pymongo, dotenv, os, and datetime.

# Useful Websites

These websites were all greatly helpful in my learning process when developing and troubleshooting this software.

- [mongodb.com](https://www.mongodb.com/docs/manual/installation/)
- [mongodb.com](https://www.mongodb.com/docs/mongodb-shell/install/)
- [youtube.com](https://youtu.be/scVi_6xqAEc)
- [mongodb.com](https://www.mongodb.com/languages/python)
- [stackoverflow.com](https://stackoverflow.com/questions/2801008/mongodb-insert-if-not-exists)
- [mongodb.com](https://www.mongodb.com/docs/manual/reference/method/db.collection.findOne/)
- [tutorialspoint.com](https://www.tutorialspoint.com/python_data_access/python_mongodb_delete_document.htm#:~:text=Deleting%20documents%20using%20python,the%20condition%20for%20deleting%20documents.)

# Future Work

As I said previously, this software isn't yet at the point where I believe it could feasibly be anything more than a simple terminal script, however, that is being worked on, and here is the future work planned to meet that goal.

- Improving input features to only allow desired inputs to be provided (other input are liable to be met with errors currently)
- Improving function structure to provide ease of understanding and less repetition within the code. Will likely be seperating any UI functions from database functions and placing them in new files for ease of debugging.
- Looping and creating a back feature so that the user may stay inside the software until they are done.
- Providing more member and admin features.
- Creating collection schemas

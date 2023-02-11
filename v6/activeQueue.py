from eloTracker import *
from databaseRequests import *

def main():
    collection = "UserData"
    activeUsers = getAllActiveUsersFromDataBase(collection)

    updateUsers(activeUsers, collection)

if __name__ == '__main__':
    main()
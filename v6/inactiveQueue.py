from eloTracker import *
from databaseRequests import *

def main():
    collection = "UserData"
    inactiveUsers = getAllInactiveUsersFromDataBase(collection)

    updateUsers(inactiveUsers, collection)

if __name__ == '__main__':
    main()
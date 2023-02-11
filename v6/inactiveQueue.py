from eloTracker import *
from databaseRequests import *

def main():
    collection = "UserTestData"
    inactiveUsers = getAllInactiveUsersFromDataBase(collection)

    updateUsers(inactiveUsers, collection)

if __name__ == '__main__':
    main()
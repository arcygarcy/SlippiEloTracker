from threading import Thread
import time
from databaseRequests import *
from slippiRequests import *

def updateUserData(id, user, collection):
    print(f'{user["tag"]:<9}|{str(user["queue"]):^8}|{" Attempting to update":<58}')
    slippiData = getUserDataFromSlippiByTag(user['tag'])
    if not slippiData['data']['getConnectCode'] is None:
        slippiDataNumer = slippiData['data']['getConnectCode']['user']['rankedNetplayProfile']['ratingOrdinal']
        if len(user['datapoints']) > 0:
            if type(slippiDataNumer) is float and not slippiDataNumer == user['datapoints'][-1]:
                user['queue'] = [0, 0]
                updateUserToDatabaseByID(id, slippiData, collection)
                print(f'{user["tag"]:<9}|{str(user["queue"]):^8}|{" Updating user elo":<58}')
            else:
                user['queue'][0] += 1 if user['queue'][0] < 7 else 0
                print(f'{user["tag"]:<9}|{str(user["queue"]):^8}|{" No new elo, incrementing inactive queue":<58}')
        else:
            print(f'{user["tag"]:<9}|{str(user["queue"]):^8}|{" Updating new user elo":<58}')
            updateUserToDatabaseByID(id, slippiData, collection)
    else:
        user['queue'][1] += 1
        print(f'{user["tag"]:<9}|{str(user["queue"]):^8}|{" Not found on slippi servers, incrementing delete":<58}')

def updateAllUsers(allUsers, collection):
    usersArray = getAllUsersFromDataBase(collection)['documents']
    for user in usersArray:
        if user['_id'] in allUsers.keys():
            allUsers[user['_id']] = {
                'tag': user['tag'],
                'datapoints': user['datapoints'],
                'characters': user['characters'],
                'wins': user['wins'] if 'wins' in user else 0,
                'losses': user['losses'] if 'losses' in user else 0,
                'peak': user['peak'] if 'peak' in user else 0,
                'queue': allUsers[user['_id']]['queue']
            }
        else:
            allUsers[user['_id']] = {
                'tag': user['tag'],
                'datapoints': user['datapoints'],
                'characters': user['characters'],
                'wins': user['wins'] if 'wins' in user else 0,
                'losses': user['losses'] if 'losses' in user else 0,
                'peak': user['peak'] if 'peak' in user else 0,
                'queue': [0, 0]
            }

    return allUsers

def printHeader(queueType, startTime):
    print('---------------------------------------------------------------------------')
    print(f'{queueType:^75}')
    print(f'{"Runtime " + str(round((time.time()-startTime)/3600, 2)) + " hours":^75}')
    print(f'{"Current time: " + time.ctime():^75}')
    print('---------------------------------------------------------------------------')
    print(f'{"TAG":<9}|{" QUEUE":<8}|{" MESSAGE":<58}')

def main():
    slowQueue = 20
    fastQueue = 4

    startTime = time.time()
    
    collection = 'UserData'

    allUsers = updateAllUsers({}, collection)

    count = 0
    while True:
        usersToPop = []
        if count%(slowQueue*60) == 0:
            printHeader('Inactive Queue', startTime)
            allUsers = updateAllUsers(allUsers, collection)
            threads = []
            for key in allUsers.keys():
                if allUsers[key]['queue'][1] > 2:
                    print(f'{allUsers[key]["tag"]:<9}|{str(allUsers[key]["queue"]):^8}|{" Deleting user from database":<58}')
                    deleteUserFromDatabaseByID(key, collection)
                    usersToPop.append(key)
                else:
                    if allUsers[key]['queue'][1] > 0 and not allUsers[key]['queue'][0] == 0:
                        allUsers[key]['queue'][1] = 0
                    t = Thread(target=updateUserData, args=(key, allUsers[key], collection))
                    threads.append(t)
                    t.start()
            for thread in threads:
                thread.join
            count = 0
        elif count%(fastQueue*60) == 0:
            printHeader('Active Queue', startTime)
            allUsers = updateAllUsers(allUsers, collection)
            threads = []
            for key in allUsers.keys():
                if allUsers[key]['queue'][1] > 2:
                    print(f'{allUsers[key]["tag"]:<9}|{str(allUsers[key]["queue"]):^8}|{" Deleting user from database":<58}')
                    deleteUserFromDatabaseByID(key, collection)
                    usersToPop.append(key)
                elif not allUsers[key]['queue'][0] > 6:
                    if allUsers[key]['queue'][1] > 0 and not allUsers[key]['queue'][0] == 0:
                        allUsers[key]['queue'][1] = 0
                    t = Thread(target=updateUserData, args=(key, allUsers[key], collection))
                    threads.append(t)
                    t.start()
            
            for thread in threads:
                thread.join

        for key in usersToPop:
            allUsers.pop(key)

        time.sleep(1)
        count+=1

if __name__ == '__main__':
    main()

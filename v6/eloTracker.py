from threading import Thread
import datetime
from databaseRequests import *
from slippiRequests import *

def log(message):
    currentTime = datetime.datetime.now().replace(microsecond=0)
    file = open('log.txt', 'a')
    file.write(str(currentTime) + ' ' + message)
    file.write('\n')
    file.close()

def updateUser(user, collection):
    slippiData = getUserDataFromSlippiByTag(user['tag'])
    if slippiData is None:
        log('Slippi API Error')
    elif slippiData['data']['getConnectCode'] is None:
        if user['delete'] == 3:
            log(user['tag'] + ' deleted from database')
            deleteUserFromDatabaseByID(user['_id'], collection)
        else:
            log(user['tag'] + ' incrementing delete')
            user['delete'] += 1
            updateUserDeleteToDataBaseByID(user['_id'], user['delete'], collection)
    else:
        if user['delete'] != 0:
            updateUserDeleteToDataBaseByID(user['_id'], 0, collection)
        currentSlippiData = slippiData['data']['getConnectCode']['user']['rankedNetplayProfile']
        if len(user['datapoints']) == 0:
            user['active'] = 0
            updateUserToDatabaseByID(user['_id'], currentSlippiData, collection)
            updateUserActiveToDataBaseByID(user['_id'], user['active'], collection)
        elif user['datapoints'][-1] != currentSlippiData['ratingOrdinal']:
            user['active'] = 0
            updateUserToDatabaseByID(user['_id'], currentSlippiData, collection)
            updateUserActiveToDataBaseByID(user['_id'], user['active'], collection)
        else:
            user['active'] += 1 if user['active'] < 7 else 0
            updateUserActiveToDataBaseByID(user['_id'], user['active'], collection)

def updateUsers(users, collection):
    log('Attempting to update ' + str(len(users['documents'])) + ' users')

    threads = []
    for user in users['documents']:
        userThread = Thread(target=updateUser, args=(user, collection,))
        threads.append(userThread)
        userThread.start()

    for userThread in threads:
        userThread.join()
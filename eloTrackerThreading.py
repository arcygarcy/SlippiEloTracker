from threading import Thread
from pymongo import MongoClient
import requests
import json
import time

# makes post request to slippi server and returns user data parsed into a dictionary (userTag='*#*')
def getUserData(userTag):
    url = 'https://gql-gateway-dot-slippi.uc.r.appspot.com/graphql'
    data = {
        "operationName": "AccountManagementPageQuery",
        "variables": {
            "cc": userTag
        },
        "query": "fragment userProfilePage on User {rankedNetplayProfile {\n    ratingOrdinal\n    ratingUpdateCount\n    wins\n    losses\n  characters {\n      character\n      gameCount}}}query AccountManagementPageQuery($cc: String!) {getConnectCode(code: $cc) {user{...userProfilePage}}}"
    }

    response = json.loads(requests.post(url, json=data).text)

    return response

# adds a user to the database
def addUser(tag):
    client = MongoClient(
        'mongodb+srv://ArcyGarcy:QsDmAEFGlugTHWVh@slippielotracker.13pbngw.mongodb.net/test')
    db = client.slippiEloTracker
    cluster = db.UserData

    data = {'tag': tag, 'datapoints': [], 'characters': []}

    response = cluster.insert_one(data)

    return response

#delete user if tag is not found on slippi servers
def deleteUser(tag):
    client = MongoClient(
        'mongodb+srv://ArcyGarcy:QsDmAEFGlugTHWVh@slippielotracker.13pbngw.mongodb.net/test')
    db = client.slippiEloTracker
    cluster = db.UserData

    data = {'tag': tag}

    response = cluster.delete_one(data)

    return response

# gets data for a specific tag
def find(tag):
    client = MongoClient(
        'mongodb+srv://ArcyGarcy:QsDmAEFGlugTHWVh@slippielotracker.13pbngw.mongodb.net/test')
    db = client.slippiEloTracker
    cluster = db.UserData

    response = cluster.find_one({'tag': tag})

    return response

# returns all of the tags
def findAllTags():
    client = MongoClient(
        'mongodb+srv://ArcyGarcy:QsDmAEFGlugTHWVh@slippielotracker.13pbngw.mongodb.net/test')
    db = client.slippiEloTracker
    cluster = db.UserData

    response = cluster.find({}, {'_id': 0, 'tag': 1})

    tags = [x['tag'] for x in response]

    return tags

# adds a new datapoint to a specified tag, data is an array of points
def addDataPoint(tag, newPoint):
    client = MongoClient(
        'mongodb+srv://ArcyGarcy:QsDmAEFGlugTHWVh@slippielotracker.13pbngw.mongodb.net/test')
    db = client.slippiEloTracker
    cluster = db.UserData

    response = cluster.update_one({'tag': tag},
                                  {'$push':
                                   {'datapoints':
                                    {
                                        '$each': [newPoint],
                                        '$slice': -100
                                    }
                                    }
                                   })

    return response

# functions that each thread uses to update data
def updateUser(tag):
    print(f'{tag} - Start Updating')

    databaseData = find(tag)
    dataFromSlippiServers = getUserData(tag)['data']['getConnectCode']

    if not dataFromSlippiServers == None:
        newPoint = float(
            dataFromSlippiServers['user']['rankedNetplayProfile']['ratingOrdinal'])
        lastPoint = databaseData['datapoints'][-1] if len(
            databaseData['datapoints']) > 0 else -1

        if newPoint != lastPoint:
            addDataPoint(tag, newPoint)

        print(f'{tag} - Done Updating')
    else:
        #Delete
        print('To Delete')
        deleteUser(tag)

# threading function
def updateDataBase():
    print(time.ctime())
    tags = findAllTags()
    threads = []
    for tag in tags:
        t = Thread(target=updateUser, args=(tag,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

def main():
    count = 0
    while True:
        time.sleep(1)
        if count == 1:
            updateDataBase()
            print('------------------------')
        elif count == 180:
            count = 0
        count += 1

if __name__ == '__main__':
    main()

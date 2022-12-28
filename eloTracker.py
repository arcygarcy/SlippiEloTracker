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
            "cc": userTag,
            "uid": userTag
        },
        "query": "fragment userProfilePage on User {\n  fbUid\n  displayName\n  connectCode {\n    code\n    __typename\n  }\n  status\n  activeSubscription {\n    level\n    hasGiftSub\n    __typename\n  }\n  rankedNetplayProfile {\n    id\n    ratingOrdinal\n    ratingUpdateCount\n    wins\n    losses\n    dailyGlobalPlacement\n    dailyRegionalPlacement\n    continent\n    characters {\n      id\n      character\n      gameCount\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nquery AccountManagementPageQuery($cc: String!, $uid: String!) {\n  getUser(fbUid: $uid) {\n    ...userProfilePage\n    __typename\n  }\n  getConnectCode(code: $cc) {\n    user {\n      ...userProfilePage\n      __typename\n    }\n    __typename\n  }\n}\n"
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

    dataFromSlippiServers = getUserData(tag)['data']['getConnectCode']

    databaseData = find(tag)

    newPoint = float(
        dataFromSlippiServers['user']['rankedNetplayProfile']['ratingOrdinal'])
    lastPoint = databaseData['datapoints'][-1] if len(
        databaseData['datapoints']) > 0 else -1

    if newPoint != lastPoint:
        addDataPoint(tag, newPoint)

    print(f'{tag} - Done Updating')

# threading function
def updateDataBase():
    print(time.ctime())
    tags = findAllTags()
    # tags = ['AF#3']
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

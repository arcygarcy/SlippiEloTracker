from threading import Thread
import requests
import json
import time

# makes post request to slippi server and returns user data parsed into a dictionary (userTag='*#*')
def getUserDataFromSlippi(tag):
    url = 'https://gql-gateway-dot-slippi.uc.r.appspot.com/graphql'
    data = {
        "operationName": "AccountManagementPageQuery",
        "variables": {
            "cc": tag
        },
        "query": "fragment userProfilePage on User {rankedNetplayProfile {\n    ratingOrdinal\n    ratingUpdateCount\n    wins\n    losses\n  characters {\n      character\n      gameCount}}}query AccountManagementPageQuery($cc: String!) {getConnectCode(code: $cc) {user{...userProfilePage}}}"
    }

    response = json.loads(requests.post(url, json=data).text)

    return response

#delete user if tag is not found on slippi servers
def deleteUserFromDatabase(tag):
    print('Deleting: ' + tag + ' from the database.')
    url = "https://data.mongodb-api.com/app/data-wterg/endpoint/data/v1/action/deleteOne"

    payload = json.dumps({
    "dataSource": "SlippiEloTracker",
    "database": "slippiEloTracker",
    "collection": "UserData",
    "filter": {
        "tag": tag
    }
    })
    headers = {
    'Content-Type': 'application/json',
    'Access-Control-Request-Headers': '*',
    'api-key': 'ZlLdccwmLobGp1zSTU08vCg3XTIFmhaJZkiQxyloWpwpWhYo3QqIsV7ISevWVd1F'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    data = json.loads(response.text)

    return data

# gets data for a specific tag
def getUserFromDataBase(tag):
    url = "https://data.mongodb-api.com/app/data-wterg/endpoint/data/v1/action/findOne"

    payload = json.dumps({
    "dataSource": "SlippiEloTracker",
    "database": "slippiEloTracker",
    "collection": "UserData",
    "filter": {
        "tag": tag
    }
    })
    headers = {
    'Content-Type': 'application/json',
    'Access-Control-Request-Headers': '*',
    'api-key': 'ZlLdccwmLobGp1zSTU08vCg3XTIFmhaJZkiQxyloWpwpWhYo3QqIsV7ISevWVd1F',
    'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    data = json.loads(response.text)

    return data

# returns all of the tags
def getAllUsersTagsFromDataBase():
    url = "https://data.mongodb-api.com/app/data-wterg/endpoint/data/v1/action/find"

    payload = json.dumps({
    "dataSource": "SlippiEloTracker",
    "database": "slippiEloTracker",
    "collection": "UserData",
    "filter": {
    }
    })
    headers = {
    'Content-Type': 'application/json',
    'Access-Control-Request-Headers': '*',
    'api-key': 'ZlLdccwmLobGp1zSTU08vCg3XTIFmhaJZkiQxyloWpwpWhYo3QqIsV7ISevWVd1F',
    'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    data = json.loads(response.text)

    tags = []
    documents = data['documents']
    for document in documents:
        tags.append(document['tag'])

    return tags

# adds a new datapoint to a specified tag, data is an array of points
def updateUserToDatabase(tag, newPoint):
    url = "https://data.mongodb-api.com/app/data-wterg/endpoint/data/v1/action/updateOne"

    payload = json.dumps({
    "dataSource": "SlippiEloTracker",
    "database": "slippiEloTracker",
    "collection": "UserData",
    "filter": {
        "tag": tag
    },
    "update": {
        "$push": {
        "datapoints": {
            "$each": [
            newPoint
            ],
            "$slice": -100
        }
        }
    }
    })
    headers = {
    'Content-Type': 'application/json',
    'Access-Control-Request-Headers': '*',
    'api-key': 'ZlLdccwmLobGp1zSTU08vCg3XTIFmhaJZkiQxyloWpwpWhYo3QqIsV7ISevWVd1F'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    data = json.loads(response.text)

    return data

def updateUser(tag):
    print(tag + ':Getting Current Rank')
    databaseData = getUserFromDataBase(tag)
    slippiData = getUserDataFromSlippi(tag)

    if not slippiData['data']['getConnectCode'] == None:
        mostRecentDatabaseRank = databaseData['document']['datapoints'][-1] if len(databaseData['document']['datapoints'])>1 else 0
        currentSlippiRank = slippiData['data']['getConnectCode']['user']['rankedNetplayProfile']['ratingOrdinal']

        if not mostRecentDatabaseRank == currentSlippiRank:
            print(tag + ':Updating current rank')
            updateUserToDatabase(tag, currentSlippiRank)
        else:
            print(tag + ':Rank is already up to date')
    else:
        print('User not found on slippi servers.')
        deleteUserFromDatabase(tag)

# threading function
def updateDataBase():
    print(time.ctime())
    tags = getAllUsersTagsFromDataBase()
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

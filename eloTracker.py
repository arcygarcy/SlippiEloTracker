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

    response = requests.request("POST", url, json=data)

    data = {'data': {'getConnectCode': None}}
    if response != None:
        data = json.loads(response.text)

    return data

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
    dataFromSlippi = getUserDataFromSlippi(tag)
    dataFromDatabase = getUserFromDataBase(tag)

    returnData = [0, 0]

    if not dataFromSlippi['data']['getConnectCode'] == None:
        mostRecentDatabaseRank = dataFromDatabase['document']['datapoints'][-1] if len(dataFromDatabase['document']['datapoints'])>0 else 0
        currentSlippiRank = dataFromSlippi['data']['getConnectCode']['user']['rankedNetplayProfile']['ratingOrdinal']

        if not mostRecentDatabaseRank == currentSlippiRank:
            updateUserToDatabase(tag, currentSlippiRank)
        else:
            returnData[0]=1
    else:
        returnData[1]=1

    return returnData

def updateUserAndQueue(tag, userData):
    updateQueueData = updateUser(tag)
    message = ''
    if not updateQueueData[0] == 0:
        userData[0] += 1 if userData[0] < 6 else 0
        message = 'Rank is Already Up to Date Adding to Slow Queue Detection'
    else:
        userData[0] = 0
        message = 'Updated Current Rank'
    if not updateQueueData[1] == 0:
        userData[1] += 1
        message = 'User Not Found on Slippi Servers Adding to Delete Detection'
    else:
        userData[1] = 0
    print(f'{tag:<10}{str(userData):<10}{message}')

def test():
    print('----------TEST----------')
    print('------TEST_COMPLETE-----')

def main():
    longQueueMinutes = 20
    shortQueueMinutes = 5

    allUsers = {}
    count = 0
    while True:
        time.sleep(1)

        if count == 0 or count%(60*shortQueueMinutes) == 0 and not count%(60*longQueueMinutes) == 0:
            print('------------------------------------------------------------------------')
            print(f'Current time: {time.ctime():<25}Short Queue')
            print('------------------------------------------------------------------------')

            for user in getAllUsersTagsFromDataBase():
                if not user in allUsers.keys():
                    allUsers[user]=[0,0]
            
            usersToDelete = []
            threads = []
            for user in allUsers.keys():
                if allUsers[user][0] < 5 and allUsers[user][1] < 5:
                    t = Thread(target=updateUserAndQueue, args=(user, allUsers[user]))
                    print(f'{user:<10}{str(allUsers[user]):<10}Updating Users Rank {t.name}')
                    threads.append(t)
                    t.start()
                elif allUsers[user][1] >= 5:
                    deleteUserFromDatabase(user)
                    usersToDelete.append(user)

            for thread in threads:
                thread.join()

            for user in usersToDelete:
                allUsers.pop(user)

        elif count%(60*longQueueMinutes) == 0:
            print('------------------------------------------------------------------------')
            print(f'Current time: {time.ctime():<25}Long Queue')
            print('------------------------------------------------------------------------')
            
            count = 0
            
            threads = []
            for user in allUsers.keys():
                t = Thread(target=updateUserAndQueue, args=(user, allUsers[user]))
                print(f'{user:<10}{str(allUsers[user]):<10}Updating Users Rank {t.name}')
                threads.append(t)
                t.start()

            for thread in threads:
                thread.join()

        count += 1

if __name__ == '__main__':
    main()

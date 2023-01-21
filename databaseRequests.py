import requests
import json

#delete user if tag is not found on slippi servers
def deleteUserFromDatabaseByID(_id, collection):
    url = "https://data.mongodb-api.com/app/data-wterg/endpoint/data/v1/action/deleteOne"

    payload = json.dumps({
        "dataSource": "SlippiEloTracker",
        "database": "slippiEloTracker",
        "collection": collection,
        "filter": {
            "_id": {'$oid': _id}
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

# returns all of the tags
def getAllUsersFromDataBase(collection):
    url = "https://data.mongodb-api.com/app/data-wterg/endpoint/data/v1/action/find"

    payload = json.dumps({
        "dataSource": "SlippiEloTracker",
        "database": "slippiEloTracker",
        "collection": collection,
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

    return data

# adds a new datapoint to a specified tag, data is an array of points
def updateUserToDatabaseByID(_id, slippiData, collection):
    url = "https://data.mongodb-api.com/app/data-wterg/endpoint/data/v1/action/updateOne"

    payload = json.dumps({
        "dataSource": "SlippiEloTracker",
        "database": "slippiEloTracker",
        "collection": collection,
        "filter": {
            "_id": {'$oid': _id}
        },
        "update": {
            "$push": {
                "datapoints": {
                    "$each": [
                        slippiData['data']['getConnectCode']['user']['rankedNetplayProfile']['ratingOrdinal']
                    ],
                    "$slice": -250
                    }
                },
                "$set": {
                    "characters": slippiData['data']['getConnectCode']['user']['rankedNetplayProfile']['characters'],
                    "wins": slippiData['data']['getConnectCode']['user']['rankedNetplayProfile']['wins'],
                    "losses": slippiData['data']['getConnectCode']['user']['rankedNetplayProfile']['losses']
                },
                "$max": {
                    "peak": slippiData['data']['getConnectCode']['user']['rankedNetplayProfile']['ratingOrdinal']
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
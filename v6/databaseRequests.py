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
def getAllInactiveUsersFromDataBase(collection):
    url = "https://data.mongodb-api.com/app/data-wterg/endpoint/data/v1/action/find"

    payload = json.dumps({
        "dataSource": "SlippiEloTracker",
        "database": "slippiEloTracker",
        "collection": collection,
        "filter": {
            "active" : {"$gt": 6}
        },
        "projection": {
            "_id": 1,
            "tag": 1,
            "datapoints": 1,
            "active": 1,
            "delete": 1
        },
        "limit": 50000
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

#gets only active users
def getAllActiveUsersFromDataBase(collection):
    url = "https://data.mongodb-api.com/app/data-wterg/endpoint/data/v1/action/find"

    payload = json.dumps({
        "dataSource": "SlippiEloTracker",
        "database": "slippiEloTracker",
        "collection": collection,
        "filter": {
            "active" : {"$lt": 7}
        },
        "projection": {
            "_id": 1,
            "tag": 1,
            "datapoints": 1,
            "active": 1,
            "delete": 1
        },
        "limit": 50000
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
                        slippiData['ratingOrdinal']
                    ],
                    "$slice": -250
                    }
                },
            "$set": {
                "characters": slippiData['characters'],
                "wins": slippiData['wins'],
                "losses": slippiData['losses']
            },
            "$max": {
                "peak": slippiData['ratingOrdinal']
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

def updateUserActiveToDataBaseByID(_id, active, collection):
    url = "https://data.mongodb-api.com/app/data-wterg/endpoint/data/v1/action/updateOne"

    payload = json.dumps({
        "dataSource": "SlippiEloTracker",
        "database": "slippiEloTracker",
        "collection": collection,
        "filter": {
            "_id": {'$oid': _id}
        },
        "update": {
            "$set": {
                "active": active
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

def updateUserDeleteToDataBaseByID(_id, delete, collection):
    url = "https://data.mongodb-api.com/app/data-wterg/endpoint/data/v1/action/updateOne"

    payload = json.dumps({
        "dataSource": "SlippiEloTracker",
        "database": "slippiEloTracker",
        "collection": collection,
        "filter": {
            "_id": {'$oid': _id}
        },
        "update": {
            "$set": {
                "delete": delete
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
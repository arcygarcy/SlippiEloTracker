import requests
import json

def getUserDataFromSlippiByTag(tag):
    url = 'https://gql-gateway-dot-slippi.uc.r.appspot.com/graphql'
    data = {
        "operationName": "AccountManagementPageQuery",
        "variables": {
            "cc": tag
        },
        "query": "fragment userProfilePage on User {rankedNetplayProfile {\n    ratingOrdinal\n    ratingUpdateCount\n    wins\n    losses\n  characters {\n      character\n      gameCount}}}query AccountManagementPageQuery($cc: String!) {getConnectCode(code: $cc) {user{...userProfilePage}}}"
    }

    response = requests.request("POST", url, json=data)

    data = None
    if response.status_code == 200:
        data = json.loads(response.text)

    return data
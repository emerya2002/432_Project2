from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
result = client['Spotify_Youtube']['songs '].aggregate([
    {
        '$match': {
            'Description': {
                '$exists': True
            }
        }
    }, {
        '$project': {
            '_id': 0, 
            'Description': 1
        }
    }, {
        '$unwind': '$Description'
    }, {
        '$project': {
            'keyPhrases': {
                '$split': [
                    '$Description', ' '
                ]
            }
        }
    }, {
        '$unwind': '$keyPhrases'
    }, {
        '$group': {
            '_id': '$keyPhrases', 
            'count': {
                '$sum': 1
            }
        }
    }, {
        '$sort': {
            'count': -1
        }
    }, {
        '$limit': 10
    }, {
        '$group': {
            '_id': None, 
            'keyPhrases': {
                '$push': '$_id'
            }
        }
    }, {
        '$project': {
            '_id': 0
        }
    }
])

for doc in result:
    print(doc['keyPhrases'])
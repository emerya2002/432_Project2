from pymongo import MongoClient

# Requires the PyMongo package.
# https://api.mongodb.com/python/current

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
            'entities': {
                '$regexFindAll': {
                    'input': '$Description', 
                    'regex': '\\b[A-Z]\\w+'
                }
            }
        }
    }
])

for doc in result:
    print(doc['entities'])
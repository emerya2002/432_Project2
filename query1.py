import re
from pymongo import MongoClient
import matplotlib.pyplot as plt

client = MongoClient('mongodb://localhost:27017/')
result = client['Spotify_Youtube']['songs'].aggregate([
    {
        "$match": {"Description": {"$exists": True, "$ne": ""}}
    },
    {
        '$project': {
            '_id': 0, 
            'Title': 1, 
            'Description': 1, 
            'Danceability': 1, 
            'Energy': 1, 
            'Valence': 1, 
            'Tempo': 1, 
            'Duration_ms': 1, 
            'Streams': 1,  
            'Views': 1, 
            'Likes': 1, 
            'Comments': 1
        }
    }, 
    {
        '$addFields': {
            'sentiment': {
                '$switch': {
                    'branches': [
                        {'case': {'$and': [{'$gt': ['$Likes', '$Comments']}, {'$regexMatch': {'input': {'$toString': '$Description'}, 'regex': '(?i)happy|good|great|awesome|positive'}}]}, 'then': 'positive'},
                        {'case': {'$and': [{'$lt': ['$Likes', '$Comments']}, {'$regexMatch': {'input': {'$toString': '$Description'}, 'regex': '(?i)sad|bad|awful|terrible|negative'}}]}, 'then': 'negative'},
                        {'case': {'$regexMatch': {'input': {'$toString': '$Description'}, 'regex': '(?i)happy|good|great|awesome|positive'}}, 'then': 'positive'},
                        {'case': {'$regexMatch': {'input': {'$toString': '$Description'}, 'regex': '(?i)sad|bad|awful|terrible|negative'}}, 'then': 'negative'},
                    ],
                    'default': 'neutral'
                }
            }
        }
    },
    {
        '$group': {
            '_id': '$sentiment',
            'avg_temp': {'$avg': '$Tempo'}  
        }
    }
])

sentiments = []
avg_tempos = []
colors = {'positive': 'blue', 'negative': 'red', 'neutral': 'green'}  
for doc in result:
    sentiments.append(doc['_id'])
    avg_tempos.append(doc['avg_temp'])

plt.bar(sentiments, avg_tempos, color=[colors[s] for s in sentiments])
plt.title('Average Tempo by Sentiment')
plt.xlabel('Sentiment')
plt.ylabel('Average Tempo')
plt.show()

client.close()

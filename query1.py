import re
from pymongo import MongoClient
import matplotlib.pyplot as plt

def sentiment(s):
    if s > 0:
        return "positive"
    elif s < 0:
        return "negative"
    else:
        return "neutral"

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
                        {'case': {'$gt': ['$Likes', '$Comments']}, 'then': 'positive'},
                        {'case': {'$lt': ['$Likes', '$Comments']}, 'then': 'negative'},
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
colors = {'positive': 'blue', 'negative': 'red', 'neutral': 'green'}  # Specify colors for each sentiment
for doc in result:
    sentiments.append(doc['_id'])
    avg_tempos.append(doc['avg_temp'])

# Plot the bar graph with specified colors
plt.bar(sentiments, avg_tempos, color=[colors[s] for s in sentiments])
plt.title('Average Tempo by Sentiment')
plt.xlabel('Sentiment')
plt.ylabel('Average Tempo')
plt.show()

client.close()

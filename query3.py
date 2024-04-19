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
            'social': {
                '$switch': {
                    'branches': [
                        {'case': {'$regexMatch': {'input': {'$toString': '$Description'}, 'regex': '(?i)@|follow|followers|following|like|share|comment'}}, 'then': 'Yes'},
                    ],
                    'default': 'No'
                }
            }
        }
    },
    {
        '$group': {
            '_id': '$social',
            "avg_views": {"$avg": "$Views"},
            "avg_likes": {"$avg": "$Likes"},
            "avg_comments": {"$avg": "$Comments"}
        }
    }
])

social_metrics = {}
non_social_metrics = {}

for doc in result:
    if doc["_id"] == "Yes":
        social_metrics = doc
    elif doc["_id"] == "No":
        non_social_metrics = doc

labels = ['Views', 'Likes', 'Comments']
social_values = [social_metrics.get("avg_views", 0), social_metrics.get("avg_likes", 0), social_metrics.get("avg_comments", 0)]
non_social_values = [non_social_metrics.get("avg_views", 0), non_social_metrics.get("avg_likes", 0), non_social_metrics.get("avg_comments", 0)]

# Plotting
x = range(len(labels))

# Plotting Views
plt.subplot(2, 2, 2)
plt.bar(['Social', 'Non-Social'], [social_values[0], non_social_values[0]])
plt.title('Average Views by Social Category')
plt.ylabel('Average Views')

# Plotting Likes
plt.subplot(2, 2, 3)
plt.bar(['Social', 'Non-Social'], [social_values[1], non_social_values[1]])
plt.title('Average Likes by Social Category')
plt.ylabel('Average Likes')

# Plotting Comments
plt.subplot(2, 2, 4)
plt.bar(['Social', 'Non-Social'], [social_values[2], non_social_values[2]])
plt.title('Average Comments by Social Category')
plt.ylabel('Average Comments')

plt.tight_layout()
plt.show()

client.close()

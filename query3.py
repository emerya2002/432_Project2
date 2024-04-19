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
width = 0.35  # Width of the bars

fig, ax = plt.subplots()

bars1 = ax.bar(x, social_values, width, label='Social')
bars2 = ax.bar([i + width for i in x], non_social_values, width, label='Non-Social')

ax.set_xlabel('Metrics')
ax.set_ylabel('Average')
ax.set_title('Average Metrics for Social vs Non-Social')
ax.set_xticks([i + 0.5 * width for i in x])
ax.set_xticklabels(labels)
ax.legend()

plt.show()

client.close()

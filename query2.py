import re
from pymongo import MongoClient
import matplotlib.pyplot as plt

client = MongoClient('mongodb://localhost:27017/')
result = client['Spotify_Youtube']['songs'].aggregate([
    {
        "$match": {"Description": {"$exists": True, "$ne": ""}}
    },
    {
        "$addFields": {
            "English_Word_Count": {
                "$size": {
                    "$filter": {
                        "input": {
                            "$regexFindAll": {
                                "input": {"$toLower": "$Description"},
                                "regex": r"\b(the|is|are|in|on|at|and|or|of|to|a|an|it|this|that|with|for|from|by|as|but|not|have|has|had|do|does|did|you|we|they|he|she|it|i|my|your|our|his|her|its|their|one|two|three|four|five|six|seven|eight|nine|ten)\b"
                            }
                        },
                        "as": "match",
                        "cond": {"$ne": ["$$match", []]}
                    }
                }
            }
        }
    },
    {
        "$addFields": {
            "Language": {
                "$cond": {"if": {"$gte": ["$English_Word_Count", 3]}, "then": "English", "else": "Non-English"}
            }
        }
    },
    {
        "$group": {
            "_id": "$Language",
            "avg_streams": {"$avg": "$Stream"},  # Changed to $avg to calculate average
            "avg_views": {"$avg": "$Views"},
            "avg_likes": {"$avg": "$Likes"},
            "avg_comments": {"$avg": "$Comments"}
        }
    }
])

# Store the averages in dictionaries for plotting
english_metrics = {}
non_english_metrics = {}

for doc in result:
    if doc["_id"] == "English":
        english_metrics = doc
    elif doc["_id"] == "Non-English":
        non_english_metrics = doc

# Plotting the results
labels = ['Streams', 'Views', 'Likes', 'Comments']
english_values = [english_metrics["avg_streams"], english_metrics["avg_views"], english_metrics["avg_likes"], english_metrics["avg_comments"]]
non_english_values = [non_english_metrics["avg_streams"], non_english_metrics["avg_views"], non_english_metrics["avg_likes"], non_english_metrics["avg_comments"]]

x = range(len(labels))

# Plotting Streams
plt.figure(figsize=(10, 8))
plt.subplot(2, 2, 1)
plt.bar(['English', 'Non-English'], [english_values[0], non_english_values[0]])
plt.title('Average Streams by Language')
plt.ylabel('Average Streams')

# Plotting Views
plt.subplot(2, 2, 2)
plt.bar(['English', 'Non-English'], [english_values[1], non_english_values[1]])
plt.title('Average Views by Language')
plt.ylabel('Average Views')

# Plotting Likes
plt.subplot(2, 2, 3)
plt.bar(['English', 'Non-English'], [english_values[2], non_english_values[2]])
plt.title('Average Likes by Language')
plt.ylabel('Average Likes')

# Plotting Comments
plt.subplot(2, 2, 4)
plt.bar(['English', 'Non-English'], [english_values[3], non_english_values[3]])
plt.title('Average Comments by Language')
plt.ylabel('Average Comments')

plt.tight_layout()
plt.show()

client.close()
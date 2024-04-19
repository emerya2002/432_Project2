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

plt.bar(x, english_values, label='English')
plt.bar([i + 0.4 for i in x], non_english_values, label='Non-English')

plt.xlabel('Metrics')
plt.ylabel('Average')
plt.title('Average Metrics by Language')
plt.xticks([i + 0.2 for i in x], labels)
plt.legend()

plt.show()

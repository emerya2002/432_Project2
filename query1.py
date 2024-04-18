import re
from pymongo import MongoClient
import matplotlib.pyplot as plt
import tabulate

keyword = "Official"
client = MongoClient('mongodb://localhost:27017/')
result = client['Spotify_Youtube']['songs '].aggregate([
    {
        '$match': {
            'Description': {
                '$regex': re.compile(keyword)
            }
        }
    }, {
        '$project': {
            'keywords': {
                '$split': [
                    '$Description', ' '
                ]
            }
        }
    }, {
        '$unwind': '$keywords'
    }, {
        '$match': {
            'keywords': {
                '$regex': re.compile(r"Official")
            }
        }
    }, {
        '$group': {
            '_id': '$keywords', 
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
        '$project': {
            'keyword': '$_id', 
            'count': 1, 
            '_id': 0
        }
    }
])

# Prepare data for plotting and tabulating
keywords = []
counts = []
table_data = []

for doc in result:
    keyword = doc['keyword']
    count = doc['count']
    keywords.append(keyword)
    counts.append(count)
    table_data.append([keyword, count])

# Plotting
plt.bar(keywords, counts)
plt.xlabel('Keywords')
plt.ylabel('Frequency')
plt.title('Top 10 Keywords in Description')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Tabulating
headers = ['Keyword', 'Count']
print(tabulate(table_data, headers=headers, tablefmt='grid'))

client.close()
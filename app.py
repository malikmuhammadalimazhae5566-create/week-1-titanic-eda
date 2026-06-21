import os
from flask import Flask, render_template_string
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import pandas as pd

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "eda_db"
COLLECTION_NAME = "titanic_cleaned"

app = Flask(__name__, static_folder='visualizations', static_url_path='/visualizations')

HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Titanic EDA Dashboard</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    h1,h2 { color: #2c3e50; }
    .cards { display: flex; flex-wrap: wrap; gap: 12px; }
    .card { border: 1px solid #dfe6e9; border-radius: 8px; padding: 16px; width: calc(50% - 16px); box-shadow: 0 2px 6px rgba(0,0,0,0.05); }
    a { color: #0984e3; text-decoration: none; }
    img { max-width: 100%; border-radius: 4px; }
    pre { background: #f5f6fa; padding: 12px; border-radius: 6px; overflow: auto; }
  </style>
</head>
<body>
  <h1>Titanic EDA Dashboard</h1>
  <p>This dashboard presents the cleaned Titanic dataset stored in MongoDB and the generated visualizations.</p>
  <h2>Run the EDA pipeline</h2>
  <p>Execute <code>python eda.py</code> first to load the Titanic data, clean it, save it into MongoDB, and generate the plots.</p>

  <h2>MongoDB connection</h2>
  <p>Using <code>{{ mongo_uri }}</code> with database <code>{{ db_name }}</code> and collection <code>{{ collection_name }}</code>.</p>

  <h2>Available Visualizations</h2>
  <div class="cards">
    {% for title, filename in plots %}
    <div class="card">
      <h3>{{ title }}</h3>
      <a href="/visualizations/{{ filename }}" target="_blank">
        <img src="/visualizations/{{ filename }}" alt="{{ title }}">
      </a>
    </div>
    {% endfor %}
  </div>

  <h2>Available API Endpoints</h2>
  <ul>
    <li><a href="/api/data">/api/data</a> - Cleaned Titanic dataset from MongoDB as JSON</li>
    <li><a href="/api/stats">/api/stats</a> - Summary statistics from the cleaned dataset</li>
  </ul>

  <h2>Summary Statistics</h2>
  <pre>{{ stats }}</pre>
</body>
</html>
"""

PLOTS = [
    ("Survival Count", "1_survival_count.png"),
    ("Survival Count by Sex", "2_survival_by_sex.png"),
    ("Distribution of Passenger Ages", "3_age_distribution.png"),
    ("Fare Distribution by Passenger Class", "4_fare_by_pclass.png"),
    ("Correlation Heatmap", "5_correlation_heatmap.png"),
]


def get_mongo_client(uri=MONGO_URI):
    return MongoClient(uri, serverSelectionTimeoutMS=5000)


def fetch_cleaned_data():
    client = get_mongo_client()
    try:
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        records = list(collection.find({}, {'_id': 0}))
        return records
    except ServerSelectionTimeoutError:
        return []
    finally:
        client.close()


def get_summary_stats():
    records = fetch_cleaned_data()
    if not records:
        return {'error': 'No data available. Run eda.py and ensure MongoDB is running.'}
    df = pd.DataFrame(records)
    stats = df.describe(include='all').transpose().to_dict()
    return stats


@app.route('/')
def home():
    stats = get_summary_stats()
    return render_template_string(
        HTML_TEMPLATE,
        mongo_uri=MONGO_URI,
        db_name=DB_NAME,
        collection_name=COLLECTION_NAME,
        plots=PLOTS,
        stats=stats,
    )


@app.route('/api/data')
def api_data():
    return {'data': fetch_cleaned_data()}


@app.route('/api/stats')
def api_stats():
    return {'stats': get_summary_stats()}


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)

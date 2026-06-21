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
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Titanic EDA Dashboard</title>
  <style>
    :root {
      --bg: #f3f6fb;
      --surface: #ffffff;
      --surface-strong: #e2e8f0;
      --text: #1f2937;
      --muted: #475569;
      --primary: #2563eb;
      --accent: #7c3aed;
      --shadow: 0 20px 50px rgba(15, 23, 42, 0.08);
    }
    * { box-sizing: border-box; }
    body { margin: 0; font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); }
    a { color: var(--primary); text-decoration: none; }
    h1, h2, h3 { margin: 0; }
    header { background: linear-gradient(135deg, #1d4ed8, #3b82f6); color: white; padding: 42px 24px; text-align: center; }
    header h1 { font-size: clamp(2rem, 4vw, 3.8rem); letter-spacing: -0.04em; }
    header p { margin-top: 16px; max-width: 760px; margin-left: auto; margin-right: auto; color: rgba(255,255,255,0.88); line-height: 1.8; }
    .container { max-width: 1180px; margin: -48px auto 40px; padding: 0 24px; }
    .panel { display: grid; grid-template-columns: 1.4fr 0.8fr; gap: 24px; margin-top: 24px; }
    .panel-card, .stats-card, .card { background: var(--surface); border-radius: 28px; padding: 28px; box-shadow: var(--shadow); }
    .panel-card h2 { font-size: 1.9rem; margin-bottom: 18px; }
    .panel-card p { color: var(--muted); line-height: 1.8; }
    .buttons { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 20px; }
    .button { display: inline-flex; align-items: center; justify-content: center; padding: 14px 22px; border-radius: 999px; font-weight: 700; transition: transform .2s ease, box-shadow .2s ease; }
    .button.primary { background: var(--primary); color: white; box-shadow: 0 16px 36px rgba(37, 99, 235, 0.24); }
    .button.secondary { background: #eff6ff; color: var(--primary); }
    .button:hover { transform: translateY(-2px); }
    .stats-grid { display: grid; gap: 18px; }
    .stat { padding: 22px; border-radius: 24px; background: #f8fafc; display: flex; flex-direction: column; gap: 8px; }
    .stat strong { font-size: 1.4rem; color: var(--text); }
    .stat span { color: var(--muted); line-height: 1.6; }
    .cards { display: grid; gap: 24px; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); margin-top: 32px; }
    .card h3 { font-size: 1.1rem; margin-bottom: 14px; }
    .card img { width: 100%; border-radius: 20px; display: block; }
    .section { margin-top: 32px; }
    .section h2 { margin-bottom: 18px; font-size: 1.85rem; }
    .notice { background: #eef2ff; border-left: 4px solid #6366f1; padding: 18px 22px; border-radius: 20px; color: var(--text); margin-top: 24px; }
    pre { margin: 0; background: #0f172a; color: white; padding: 20px; border-radius: 20px; overflow-x: auto; font-size: 0.95rem; line-height: 1.6; }
    table { width: 100%; border-collapse: collapse; margin-top: 16px; }
    th, td { padding: 12px 14px; text-align: left; border-bottom: 1px solid #e2e8f0; }
    th { color: var(--muted); font-weight: 700; }
    td { color: var(--text); }
    .grid-wide { display: grid; gap: 24px; grid-template-columns: 1fr 1fr; }
    @media (max-width: 900px) { .panel, .grid-wide { grid-template-columns: 1fr; } }
    @media (max-width: 620px) { header { padding: 32px 18px; } .container { padding: 0 16px; } }
  </style>
</head>
<body>
  <header>
    <h1>Titanic EDA Dashboard</h1>
    <p>Explore cleaned Titanic data, visualizations, and MongoDB results from a Flask backend.</p>
  </header>
  <div class="container">
    <div class="panel">
      <div class="panel-card">
        <h2>App summary</h2>
        <p>Run <code>python eda.py</code> to clean the Titanic dataset, save it into MongoDB, and generate five key visualizations. Then launch the dashboard with <code>python app.py</code> for local exploration.</p>
        <div class="buttons">
          <a class="button primary" href="/api/data">View JSON data</a>
          <a class="button secondary" href="/api/stats">View stats</a>
        </div>
        <div class="notice">
          MongoDB connection: <strong>{{ mongo_uri }}</strong><br>
          Database: <strong>{{ db_name }}</strong><br>
          Collection: <strong>{{ collection_name }}</strong>
        </div>
      </div>
      <div class="stats-card">
        <div class="stats-grid">
          <div class="stat"><strong>5 Visualizations</strong><span>Survival, gender, age, fare class, and correlation heatmap.</span></div>
          <div class="stat"><strong>891 Records</strong><span>Classic Titanic passenger dataset cleaned and stored.</span></div>
          <div class="stat"><strong>MongoDB Ready</strong><span>Cleaned dataset is persisted for API access and future queries.</span></div>
        </div>
      </div>
    </div>

    <section class="section">
      <div class="grid-wide">
        <div class="card">
          <h3>Available API Endpoints</h3>
          <table>
            <thead>
              <tr><th>Endpoint</th><th>Description</th></tr>
            </thead>
            <tbody>
              <tr><td><a href="/api/data">/api/data</a></td><td>Cleaned Titanic data in JSON format</td></tr>
              <tr><td><a href="/api/stats">/api/stats</a></td><td>Summary statistics for cleaned data</td></tr>
            </tbody>
          </table>
        </div>
        <div class="card">
          <h3>Quick start</h3>
          <pre>pip install -r requirements.txt
python eda.py
python app.py
</pre>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Visualizations</h2>
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
    </section>
  </div>
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

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
      --bg: #020617;
      --surface: rgba(18, 23, 43, 0.96);
      --surface-soft: rgba(15, 23, 42, 0.78);
      --text: #e2e8f0;
      --muted: #94a3b8;
      --primary: #38bdf8;
      --primary-soft: rgba(56, 189, 248, 0.14);
      --accent: #a855f7;
      --shadow: 0 32px 80px rgba(15, 23, 42, 0.35);
      --border: rgba(148, 163, 184, 0.18);
    }
    * { box-sizing: border-box; }
    body { margin: 0; font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: radial-gradient(circle at top, rgba(56, 189, 248, 0.12), transparent 32%), linear-gradient(180deg, #020617 0%, #070f1f 100%); color: var(--text); }
    a { color: var(--primary); text-decoration: none; }
    h1, h2, h3 { margin: 0; }
    header { padding: 42px 22px 26px; text-align: center; }
    header h1 { font-size: clamp(2.8rem, 5vw, 4.8rem); letter-spacing: -0.05em; }
    header p { margin: 18px auto 0; max-width: 760px; color: var(--muted); font-size: 1.05rem; line-height: 1.8; }
    .container { max-width: 1180px; margin: 0 auto 40px; padding: 0 22px; }
    .panel { display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 24px; align-items: start; margin-top: 24px; }
    .panel-card, .stats-card, .card, .chart-card, .deployment-card, .notice { background: var(--surface); border: 1px solid var(--border); border-radius: 32px; box-shadow: var(--shadow); backdrop-filter: blur(18px); }
    .panel-card, .chart-card, .deployment-card { padding: 32px; }
    .panel-card h2 { font-size: 2rem; margin-bottom: 18px; }
    .panel-card p { color: var(--muted); line-height: 1.8; }
    .button-row { display: flex; flex-wrap: wrap; gap: 16px; margin-top: 28px; }
    .button { display: inline-flex; align-items: center; justify-content: center; min-width: 160px; padding: 16px 24px; border-radius: 999px; font-weight: 700; transition: transform 0.2s ease, box-shadow 0.2s ease; }
    .button.primary { background: linear-gradient(135deg, #38bdf8, #0ea5e9); color: white; box-shadow: 0 18px 40px rgba(56, 189, 248, 0.24); }
    .button.secondary { background: rgba(255,255,255,0.08); color: var(--text); }
    .button:hover { transform: translateY(-2px); }
    .stats-grid { display: grid; gap: 18px; }
    .stat { padding: 24px; border-radius: 28px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); }
    .stat strong { font-size: 1.5rem; display: block; margin-bottom: 10px; }
    .stat span { color: var(--muted); line-height: 1.8; }
    .notice { padding: 24px; margin-top: 32px; border-left: 4px solid rgba(56, 189, 248, 0.9); }
    .notice strong { color: white; }
    .section { margin-top: 38px; }
    .section h2 { font-size: 2rem; margin-bottom: 22px; }
    .grid { display: grid; gap: 24px; }
    .chart-grid { grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); }
    .chart-card { padding: 28px; }
    .chart-card h3 { margin-bottom: 18px; font-size: 1.2rem; }
    .chart-card img { width: 100%; border-radius: 24px; display: block; }
    .deployment-card p { color: var(--muted); line-height: 1.8; margin: 0; }
    .footer { text-align: center; margin-top: 48px; color: var(--muted); font-size: 0.95rem; }
    .footer a { color: var(--primary); }
    @media (max-width: 980px) { .panel { grid-template-columns: 1fr; } }
    @media (max-width: 720px) { .button-row { flex-direction: column; width: 100%; } }
  </style>
</head>
<body>
  <header>
    <h1>Titanic EDA Dashboard</h1>
    <p>Visualize Titanic data with a polished dashboard, MongoDB support, and intuitive charts.</p>
  </header>
  <div class="container">
    <div class="panel">
      <div class="panel-card">
        <h2>Project summary</h2>
        <p>Run <code>python eda.py</code> to clean Titanic passenger data, generate meaningful plots, and save the cleaned dataset to MongoDB. Start the app with <code>python app.py</code> for local exploration.</p>
        <div class="button-row">
          <a class="button primary" href="/api/data">View JSON data</a>
          <a class="button secondary" href="/api/stats">View stats</a>
        </div>
        <div class="notice">
          MongoDB URI: <strong>{{ mongo_uri }}</strong><br>
          Database: <strong>{{ db_name }}</strong><br>
          Collection: <strong>{{ collection_name }}</strong>
        </div>
      </div>
      <div class="stats-card">
        <div class="stats-grid">
          <div class="stat"><strong>5 visualizations</strong><span>Survival, gender, age distribution, fare class, and correlation analysis.</span></div>
          <div class="stat"><strong>891 records</strong><span>Classic Titanic dataset cleaned and stored.</span></div>
          <div class="stat"><strong>MongoDB ready</strong><span>Cleaned data is persisted and available for API access.</span></div>
        </div>
      </div>
    </div>

    <section class="section">
      <div class="notice">
        <strong>Note:</strong> This dashboard is styled for a premium experience. The Flask backend is available locally at <a href="http://127.0.0.1:5000">http://127.0.0.1:5000</a> once the app and MongoDB are running.
      </div>
    </section>

    <section class="section">
      <h2>Visualizations</h2>
      <div class="chart-grid">
        {% for title, filename in plots %}
        <div class="chart-card">
          <h3>{{ title }}</h3>
          <a href="/visualizations/{{ filename }}" target="_blank">
            <img src="/visualizations/{{ filename }}" alt="{{ title }}">
          </a>
        </div>
        {% endfor %}
      </div>
    </section>

    <section class="section">
      <div class="deployment-card">
        <h2>Ready for deploy</h2>
        <p>This application is ready for deployment on Render, Railway, or Fly.io. The static preview is ideal for GitHub Pages while the Flask app provides the local dynamic backend.</p>
      </div>
    </section>

    <footer class="footer">
      <p>Repo: <a href="https://github.com/malikmuhammadalimazhae5566-create/week-1-titanic-eda" target="_blank">week-1-titanic-eda</a></p>
    </footer>
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

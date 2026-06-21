# Titanic EDA with MongoDB and Flask

This project performs Exploratory Data Analysis (EDA) on the Titanic dataset, cleans the data, stores it in MongoDB, generates visualizations, and serves a simple dashboard on localhost.

## Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Start MongoDB locally.
2. Run the EDA script:

```bash
python eda.py
```

3. Start the Flask app:

```bash
python app.py
```

4. Open the browser at `http://127.0.0.1:5000`.

## Files

- `eda.py`: loads Titanic data from seaborn, cleans missing values, saves data to MongoDB, and generates visualizations.
- `app.py`: Flask app to display generated plots and serve the cleaned data from MongoDB.
- `visualizations/`: folder for output images.
- `EDA_Report.md`: EDA report with findings.
- `index.html`: placeholder landing page.

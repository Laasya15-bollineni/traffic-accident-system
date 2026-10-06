# Traffic Accident Data Analysis & Visualization System

Implements the pipeline from the presentation:
Data Sources -> Cleaning -> Storage -> Analysis -> Dashboard

## Run (any laptop with Python 3.9+; VS Code terminal, PyCharm, or Command Prompt)
```bash
cd traffic_accident_system
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt

python generate_data.py        # 1. create ~50,000 sample records
python clean_data.py           # 2+3. clean + store (CSV + SQLite)
python analysis.py             # 4. print findings, save charts/summary.png
streamlit run app.py           # 5. dashboard opens at http://localhost:8501
```

## Real data
Download a Kaggle "India road accidents" / "US Accidents" CSV, put it at
`data/raw_accidents.csv` (or upload it in the dashboard sidebar). It needs columns:
`date, time, state, city, latitude, longitude, weather, road_type, vehicle_type, cause, severity, casualties`
(rename columns in `clean_data.py` if yours differ).

## Files
| File | Slide stage |
|---|---|
| generate_data.py | Data collection |
| clean_data.py | Cleaning + storage |
| analysis.py | Analysis |
| app.py | Visualization dashboard |

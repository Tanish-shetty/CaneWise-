import json
import os
from pathlib import Path
import sqlite3
from datetime import datetime, timezone
import pandas as pd
from config.settings import DB, DATA

def connect(path=None):
    path = Path(path) if path is not None else Path(os.environ.get("CANEWISE_DB", str(DB)))
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path, timeout=15)
    con.execute('PRAGMA foreign_keys=ON')
    return con

def initialize(path=None):
    with connect(path) as con:
        con.executescript('''
        CREATE TABLE IF NOT EXISTS farmers (farmer_id TEXT PRIMARY KEY, farmer_name TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS plots (plot_id TEXT PRIMARY KEY, farmer_id TEXT REFERENCES farmers,
        area_hectares REAL, soil_type TEXT, variety TEXT, planting_date TEXT, crop_growth_stage TEXT, irrigation_method TEXT);
        CREATE TABLE IF NOT EXISTS advisories (id INTEGER PRIMARY KEY, created_at TEXT NOT NULL,
        plot_id TEXT REFERENCES plots, inputs_json TEXT NOT NULL, result_json TEXT NOT NULL,
        source TEXT NOT NULL, model_version TEXT NOT NULL);
        ''')
        for n in range(1, 31):
            farmer = f'F{(n-1)//5+1:02}'
            con.execute('INSERT OR IGNORE INTO farmers VALUES (?,?)', (farmer, f'Demo Farmer {(n-1)//5+1}'))
            con.execute('INSERT OR IGNORE INTO plots VALUES (?,?,?,?,?,?,?,?)',
                        (f'P{n:02}', farmer, round(.8 + n * .1, 1), ['Sandy', 'Loamy', 'Clay'][(n-1)%3],
                         ['Co 86032', 'CoM 0265'][n%2], '2026-01-01', 'Grand growth', ['Drip', 'Furrow'][(n-1)%2]))

def plots(path=None):
    with connect(path) as con:
        return pd.read_sql_query('SELECT * FROM plots JOIN farmers USING(farmer_id)', con)

def save(plot_id, values, result, model_version, source='manual prototype input', path=None):
    with connect(path) as con:
        cursor = con.execute('INSERT INTO advisories(created_at,plot_id,inputs_json,result_json,source,model_version) VALUES (?,?,?,?,?,?)',
                             (datetime.now(timezone.utc).isoformat(), plot_id, json.dumps(values, allow_nan=False),
                              json.dumps(result, allow_nan=False), source, model_version))
        return cursor.lastrowid

def history(plot_id=None, path=None):
    with connect(path) as con:
        query = 'SELECT * FROM advisories'
        frame = pd.read_sql_query(query + (' WHERE plot_id=?' if plot_id else '') + ' ORDER BY created_at', con,
                                  params=(plot_id,) if plot_id else ())
    rows = []
    for row in frame.to_dict('records'):
        inputs = json.loads(row.pop('inputs_json'))
        result = json.loads(row.pop('result_json'))
        result.pop('alerts', None)
        rows.append({**row, **inputs, **result})
    return pd.DataFrame(rows)

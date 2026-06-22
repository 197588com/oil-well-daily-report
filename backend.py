import sqlite3
import json
import os
import csv
import io
from datetime import datetime
from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# 数据库路径：Windows 放在 exe 同级目录；Android 放在 app 私有目录
if os.environ.get('ANDROID_PRIVATE'):
    DB_DIR = os.environ.get('ANDROID_PRIVATE')
else:
    DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, 'oil_well.db')

# ===================== 数据库初始化 =====================
def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS well_data (
            well_name TEXT,
            day INTEGER,
            date TEXT,
            pressure REAL,
            temp REAL,
            water_ratio REAL,
            gas_meter_2 REAL,
            liquid REAL,
            oil REAL,
            water REAL,
            gas REAL,
            cum_oil REAL,
            cum_water REAL,
            cum_gas REAL,
            PRIMARY KEY (well_name, date)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS well_coeff (
            well_name TEXT PRIMARY KEY,
            liquid REAL,
            gas_type TEXT,
            gas_factor REAL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS well_names (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS daily_notes (
            date TEXT PRIMARY KEY,
            note TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_default_data():
    """如果数据库为空，插入默认示例数据"""
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM well_names')
    if c.fetchone()[0] > 0:
        conn.close()
        return
    
    default_data = {
        "渤页平5": [
            {"day":1,"date":"2026-06-15","pressure":9.03,"temp":22.05,"water_ratio":61.53,"gas_meter_2":32415054,"liquid":24.38,"oil":9.39,"water":14.99,"gas":18580,"cum_oil":35963.09,"cum_water":86182.56,"cum_gas":34449265},
            {"day":2,"date":"2026-06-16","pressure":5.91,"temp":22.05,"water_ratio":60.23,"gas_meter_2":32433634,"liquid":15.96,"oil":6.35,"water":9.61,"gas":18580,"cum_oil":35969.39,"cum_water":86192.95,"cum_gas":34467875},
            {"day":3,"date":"2026-06-17","pressure":6.16,"temp":22,"water_ratio":60.23,"gas_meter_2":32452120,"liquid":16.63,"oil":6.61,"water":10.02,"gas":18486,"cum_oil":35976.0,"cum_water":86202.97,"cum_gas":34476703},
            {"day":4,"date":"2026-06-18","pressure":5.88,"temp":22,"water_ratio":60.19,"gas_meter_2":32470796,"liquid":15.88,"oil":6.32,"water":9.56,"gas":18676,"cum_oil":35982.32,"cum_water":86212.53,"cum_gas":34485899},
            {"day":5,"date":"2026-06-20","pressure":5.97,"temp":22.43,"water_ratio":60.23,"gas_meter_2":32486600,"liquid":16.12,"oil":6.41,"water":9.71,"gas":15804,"cum_oil":35988.73,"cum_water":86222.24,"cum_gas":34501703}
        ],
        "义页1-1VF": [
            {"day":1,"date":"2026-06-15","pressure":0.91,"temp":18,"water_ratio":61.0,"gas_meter_2":0,"liquid":1.0,"oil":0.39,"water":0.61,"gas":295,"cum_oil":6530.2,"cum_water":23099.01,"cum_gas":7455665},
            {"day":2,"date":"2026-06-16","pressure":1.0,"temp":18,"water_ratio":60.88,"gas_meter_2":0,"liquid":1.3,"oil":0.51,"water":0.79,"gas":403,"cum_oil":6530.75,"cum_water":23099.86,"cum_gas":7456100},
            {"day":3,"date":"2026-06-17","pressure":1.08,"temp":18,"water_ratio":60.88,"gas_meter_2":0,"liquid":1.4,"oil":0.55,"water":0.85,"gas":435,"cum_oil":6531.56,"cum_water":23101.13,"cum_gas":7456745},
            {"day":4,"date":"2026-06-18","pressure":1.6,"temp":18,"water_ratio":61.01,"gas_meter_2":0,"liquid":2.08,"oil":0.81,"water":1.27,"gas":645,"cum_oil":6532.37,"cum_water":23102.4,"cum_gas":7457390},
            {"day":5,"date":"2026-06-20","pressure":1.95,"temp":18,"water_ratio":60.88,"gas_meter_2":0,"liquid":2.67,"oil":1.04,"water":1.63,"gas":786,"cum_oil":6533.41,"cum_water":23104.03,"cum_gas":7458176}
        ],
        "义页1-2HF": [
            {"day":1,"date":"2026-06-15","pressure":9.85,"temp":28.3,"water_ratio":85.83,"gas_meter_2":0,"liquid":23.64,"oil":3.35,"water":20.29,"gas":18222,"cum_oil":10409.68,"cum_water":56833.53,"cum_gas":33373681},
            {"day":2,"date":"2026-06-16","pressure":9.86,"temp":28,"water_ratio":85.83,"gas_meter_2":0,"liquid":23.66,"oil":3.35,"water":20.31,"gas":18241,"cum_oil":10413.03,"cum_water":56853.84,"cum_gas":33391922},
            {"day":3,"date":"2026-06-17","pressure":9.87,"temp":28,"water_ratio":85.86,"gas_meter_2":0,"liquid":23.69,"oil":3.35,"water":20.34,"gas":18260,"cum_oil":10416.38,"cum_water":56874.18,"cum_gas":33410182},
            {"day":4,"date":"2026-06-18","pressure":9.87,"temp":28,"water_ratio":85.86,"gas_meter_2":0,"liquid":23.69,"oil":3.35,"water":20.34,"gas":18260,"cum_oil":10419.73,"cum_water":56894.52,"cum_gas":33428443},
            {"day":5,"date":"2026-06-20","pressure":9.84,"temp":28.23,"water_ratio":85.86,"gas_meter_2":0,"liquid":23.62,"oil":3.34,"water":20.28,"gas":18204,"cum_oil":10423.07,"cum_water":56914.8,"cum_gas":33446647}
        ]
    }
    default_coeff = {
        "渤页平5": {"liquid": 2.7, "gas_type": "diff", "gas_factor": 0},
        "义页1-1VF": {"liquid": 1.37, "gas_type": "multiply", "gas_factor": 403},
        "义页1-2HF": {"liquid": 2.4, "gas_type": "multiply", "gas_factor": 1850}
    }
    
    for well, rows in default_data.items():
        c.execute('INSERT OR IGNORE INTO well_names (name) VALUES (?)', (well,))
        for row in rows:
            c.execute('''
                INSERT OR REPLACE INTO well_data 
                (well_name, day, date, pressure, temp, water_ratio, gas_meter_2, liquid, oil, water, gas, cum_oil, cum_water, cum_gas)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (well, row['day'], row['date'], row['pressure'], row['temp'], 
                  row['water_ratio'], row.get('gas_meter_2', 0), row['liquid'], 
                  row['oil'], row['water'], row['gas'], row['cum_oil'], 
                  row['cum_water'], row['cum_gas']))
    
    for well, coeff in default_coeff.items():
        c.execute('''
            INSERT OR REPLACE INTO well_coeff (well_name, liquid, gas_type, gas_factor)
            VALUES (?, ?, ?, ?)
        ''', (well, coeff['liquid'], coeff['gas_type'], coeff['gas_factor']))
    
    conn.commit()
    conn.close()

# ===================== API 路由 =====================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    conn = get_db()
    c = conn.cursor()
    
    c.execute('SELECT name FROM well_names ORDER BY id')
    wells = [row['name'] for row in c.fetchall()]
    
    data = {}
    for well in wells:
        c.execute('SELECT * FROM well_data WHERE well_name = ? ORDER BY date', (well,))
        rows = []
        for row in c.fetchall():
            rows.append({
                'day': row['day'], 'date': row['date'], 'pressure': row['pressure'],
                'temp': row['temp'], 'water_ratio': row['water_ratio'],
                'gas_meter_2': row['gas_meter_2'], 'liquid': row['liquid'],
                'oil': row['oil'], 'water': row['water'], 'gas': row['gas'],
                'cum_oil': row['cum_oil'], 'cum_water': row['cum_water'], 'cum_gas': row['cum_gas']
            })
        data[well] = rows
    
    coeff = {}
    c.execute('SELECT * FROM well_coeff')
    for row in c.fetchall():
        coeff[row['well_name']] = {
            'liquid': row['liquid'],
            'gas_type': row['gas_type'],
            'gas_factor': row['gas_factor']
        }
    
    conn.close()
    return jsonify({'wells': wells, 'data': data, 'coeff': coeff})

@app.route('/api/data', methods=['POST'])
def save_data():
    payload = request.json
    conn = get_db()
    c = conn.cursor()
    
    # 保存井名
    for well in payload.get('wells', []):
        c.execute('INSERT OR IGNORE INTO well_names (name) VALUES (?)', (well,))
    
    # 保存数据
    for well, rows in payload.get('data', {}).items():
        for row in rows:
            c.execute('''
                INSERT OR REPLACE INTO well_data 
                (well_name, day, date, pressure, temp, water_ratio, gas_meter_2, liquid, oil, water, gas, cum_oil, cum_water, cum_gas)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (well, row['day'], row['date'], row['pressure'], row['temp'], 
                  row['water_ratio'], row.get('gas_meter_2', 0), row['liquid'], 
                  row['oil'], row['water'], row['gas'], row['cum_oil'], 
                  row['cum_water'], row['cum_gas']))
    
    # 保存系数
    for well, coeff in payload.get('coeff', {}).items():
        c.execute('''
            INSERT OR REPLACE INTO well_coeff (well_name, liquid, gas_type, gas_factor)
            VALUES (?, ?, ?, ?)
        ''', (well, coeff['liquid'], coeff['gas_type'], coeff['gas_factor']))
    
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/well', methods=['POST'])
def add_well():
    payload = request.json
    well_name = payload.get('name')
    if not well_name:
        return jsonify({'success': False, 'error': 'Name required'}), 400
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO well_names (name) VALUES (?)', (well_name,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/well/<well_name>', methods=['DELETE'])
def delete_well(well_name):
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM well_data WHERE well_name = ?', (well_name,))
    c.execute('DELETE FROM well_coeff WHERE well_name = ?', (well_name,))
    c.execute('DELETE FROM well_names WHERE name = ?', (well_name,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/well/<well_name>/record/<date>', methods=['DELETE'])
def delete_record(well_name, date):
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM well_data WHERE well_name = ? AND date = ?', (well_name, date))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/note/<date>', methods=['GET'])
def get_note(date):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT note FROM daily_notes WHERE date = ?', (date,))
    row = c.fetchone()
    conn.close()
    return jsonify({'note': row['note'] if row else ''})

@app.route('/api/note/<date>', methods=['POST'])
def save_note(date):
    payload = request.json
    note = payload.get('note', '')
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO daily_notes (date, note) VALUES (?, ?)', (date, note))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/export/csv')
def export_csv():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT name FROM well_names ORDER BY id')
    wells = [row['name'] for row in c.fetchall()]
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['井号','日期','压力(MPa)','出液温度(℃)','液量(t)','油量(t)','水量(t)','含水(%)','气量(m³)','累计油(t)','累计水(t)','累计气(m³)'])
    
    for well in wells:
        c.execute('SELECT * FROM well_data WHERE well_name = ? ORDER BY date', (well,))
        for row in c.fetchall():
            writer.writerow([well, row['date'], row['pressure'], row['temp'], row['liquid'], row['oil'], row['water'], row['water_ratio'], row['gas'], row['cum_oil'], row['cum_water'], row['cum_gas']])
    
    conn.close()
    csv_content = '\ufeff' + output.getvalue()
    return Response(csv_content, mimetype='text/csv; charset=utf-8', headers={'Content-Disposition': 'attachment; filename=oil_report.csv'})

@app.route('/api/export/json')
def export_json():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT name FROM well_names ORDER BY id')
    wells = [row['name'] for row in c.fetchall()]
    
    data = {}
    for well in wells:
        c.execute('SELECT * FROM well_data WHERE well_name = ? ORDER BY date', (well,))
        rows = []
        for row in c.fetchall():
            rows.append({
                'day': row['day'], 'date': row['date'], 'pressure': row['pressure'],
                'temp': row['temp'], 'water_ratio': row['water_ratio'],
                'gas_meter_2': row['gas_meter_2'], 'liquid': row['liquid'],
                'oil': row['oil'], 'water': row['water'], 'gas': row['gas'],
                'cum_oil': row['cum_oil'], 'cum_water': row['cum_water'], 'cum_gas': row['cum_gas']
            })
        data[well] = rows
    
    coeff = {}
    c.execute('SELECT * FROM well_coeff')
    for row in c.fetchall():
        coeff[row['well_name']] = {
            'liquid': row['liquid'],
            'gas_type': row['gas_type'],
            'gas_factor': row['gas_factor']
        }
    
    conn.close()
    backup = {
        'version': 2,
        'export_date': datetime.now().isoformat(),
        'wells': wells,
        'data': data,
        'coeff': coeff
    }
    return jsonify(backup)

@app.route('/api/import/json', methods=['POST'])
def import_json():
    payload = request.json
    conn = get_db()
    c = conn.cursor()
    
    for well in payload.get('wells', []):
        c.execute('INSERT OR IGNORE INTO well_names (name) VALUES (?)', (well,))
    
    for well, rows in payload.get('data', {}).items():
        c.execute('INSERT OR IGNORE INTO well_names (name) VALUES (?)', (well,))
        for row in rows:
            c.execute('''
                INSERT OR REPLACE INTO well_data 
                (well_name, day, date, pressure, temp, water_ratio, gas_meter_2, liquid, oil, water, gas, cum_oil, cum_water, cum_gas)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (well, row['day'], row['date'], row['pressure'], row['temp'], 
                  row['water_ratio'], row.get('gas_meter_2', 0), row['liquid'], 
                  row['oil'], row['water'], row['gas'], row['cum_oil'], 
                  row['cum_water'], row['cum_gas']))
    
    for well, coeff in payload.get('coeff', {}).items():
        c.execute('INSERT OR IGNORE INTO well_names (name) VALUES (?)', (well,))
        c.execute('''
            INSERT OR REPLACE INTO well_coeff (well_name, liquid, gas_type, gas_factor)
            VALUES (?, ?, ?, ?)
        ''', (well, coeff['liquid'], coeff['gas_type'], coeff['gas_factor']))
    
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# ===================== 启动 =====================
def run_app(host='127.0.0.1', port=0):
    """port=0 表示自动分配端口，返回实际端口"""
    init_db()
    insert_default_data()
    
    # 使用 socket 获取可用端口
    if port == 0:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((host, 0))
        port = sock.getsockname()[1]
        sock.close()
    
    def run():
        app.run(host=host, port=port, debug=False, threaded=True, use_reloader=False)
    
    return port, run

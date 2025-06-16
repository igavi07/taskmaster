import sqlite3
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

class DataStorage:

    def __init__(self, db_path: str = "data/taskmaster.db"):
        self.db_path = db_path

        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        self._init_db()

    def _init_db(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            cpu_percent REAL,
            memory_percent REAL,
            disk_percent REAL,
            data JSON
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS process_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            pid INTEGER,
            name TEXT,
            cpu_percent REAL,
            memory_mb REAL,
            threads INTEGER,
            data JSON
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            event_type TEXT,
            description TEXT,
            data JSON
        )
        ''')

        conn.commit()
        conn.close()

    def log_system_snapshot(self, system_data: Dict[str, Any]) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        timestamp = datetime.now().isoformat()
        cpu_percent = system_data.get('cpu_percent', 0)
        memory_percent = system_data.get('memory_percent', 0)
        disk_percent = system_data.get('disk_percent', 0)
        data_json = json.dumps(system_data)

        cursor.execute(
            '''
            INSERT INTO system_snapshots
            (timestamp, cpu_percent, memory_percent, disk_percent, data)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (timestamp, cpu_percent, memory_percent, disk_percent, data_json)
        )

        conn.commit()
        conn.close()

    def log_process_snapshot(self, process_data: Dict[str, Any]) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        timestamp = datetime.now().isoformat()
        pid = process_data.get('pid', 0)
        name = process_data.get('name', '')
        cpu_percent = process_data.get('cpu_percent', 0)
        memory_mb = process_data.get('memory_mb', 0)
        threads = process_data.get('threads', 0)
        data_json = json.dumps(process_data)

        cursor.execute(
            '''
            INSERT INTO process_snapshots
            (timestamp, pid, name, cpu_percent, memory_mb, threads, data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''',
            (timestamp, pid, name, cpu_percent, memory_mb, threads, data_json)
        )

        conn.commit()
        conn.close()

    def log_event(self, event_type: str, description: str, data: Dict[str, Any] = None) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        timestamp = datetime.now().isoformat()
        data_json = json.dumps(data) if data else '{}'

        cursor.execute(
            '''
            INSERT INTO events
            (timestamp, event_type, description, data)
            VALUES (?, ?, ?, ?)
            ''',
            (timestamp, event_type, description, data_json)
        )

        conn.commit()
        conn.close()

    def get_system_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        timestamp_limit = (datetime.now() - datetime.timedelta(hours=hours)).isoformat()

        cursor.execute(
            '''
            SELECT * FROM system_snapshots
            WHERE timestamp > ?
            ORDER BY timestamp
            ''',
            (timestamp_limit,)
        )

        results = []
        for row in cursor.fetchall():
            data = dict(row)
            data['data'] = json.loads(data['data'])
            results.append(data)

        conn.close()
        return results

    def get_process_history(self, pid: int, hours: int = 24) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        timestamp_limit = (datetime.now() - datetime.timedelta(hours=hours)).isoformat()

        cursor.execute(
            '''
            SELECT * FROM process_snapshots
            WHERE pid = ? AND timestamp > ?
            ORDER BY timestamp
            ''',
            (pid, timestamp_limit)
        )

        results = []
        for row in cursor.fetchall():
            data = dict(row)
            data['data'] = json.loads(data['data'])
            results.append(data)

        conn.close()
        return results

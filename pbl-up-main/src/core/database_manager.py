import sqlite3
import os
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional

class DatabaseManager:

    def __init__(self, db_path: str = "data/taskmaster.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        self.db_path = db_path
        self.conn = None
        self.initialize_database()

    def initialize_database(self) -> None:
        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS process_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                pid INTEGER NOT NULL,
                name TEXT NOT NULL,
                cpu_percent REAL,
                memory_mb REAL,
                status TEXT,
                username TEXT
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                cpu_percent REAL,
                memory_percent REAL,
                disk_percent REAL,
                total_processes INTEGER
            )
            ''')

            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")

    def store_process_data(self, processes: List[Dict[str, Any]]) -> None:
        if not self.conn:
            self.initialize_database()

        try:
            cursor = self.conn.cursor()
            timestamp = datetime.now().isoformat()

            for process in processes:
                cursor.execute('''
                INSERT INTO process_history
                (timestamp, pid, name, cpu_percent, memory_mb, status, username)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    timestamp,
                    process.get('pid', 0),
                    process.get('name', ''),
                    process.get('cpu_percent', 0.0),
                    process.get('memory_mb', 0.0),
                    process.get('status', ''),
                    process.get('username', '')
                ))

            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error storing process data: {e}")

    def store_system_data(self, system_data: Dict[str, Any]) -> None:
        if not self.conn:
            self.initialize_database()

        try:
            cursor = self.conn.cursor()
            timestamp = datetime.now().isoformat()

            cursor.execute('''
            INSERT INTO system_history
            (timestamp, cpu_percent, memory_percent, disk_percent, total_processes)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                timestamp,
                system_data.get('cpu_percent', 0.0),
                system_data.get('memory_percent', 0.0),
                system_data.get('disk_percent', 0.0),
                system_data.get('total_processes', 0)
            ))

            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error storing system data: {e}")

    def get_process_history(self, pid: Optional[int] = None,
                           limit: int = 100) -> pd.DataFrame:
        if not self.conn:
            self.initialize_database()

        try:
            query = "SELECT * FROM process_history"
            params = []

            if pid is not None:
                query += " WHERE pid = ?"
                params.append(pid)

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            df = pd.read_sql_query(query, self.conn, params=params)

            df['timestamp'] = pd.to_datetime(df['timestamp'])

            return df
        except (sqlite3.Error, pd.errors.DatabaseError) as e:
            print(f"Error retrieving process history: {e}")
            return pd.DataFrame()

    def get_system_history(self, hours: int = 24) -> pd.DataFrame:
        if not self.conn:
            self.initialize_database()

        try:
            time_limit = (datetime.now() - pd.Timedelta(hours=hours)).isoformat()

            query = """
            SELECT * FROM system_history
            WHERE timestamp > ?
            ORDER BY timestamp
            """

            df = pd.read_sql_query(query, self.conn, params=[time_limit])

            df['timestamp'] = pd.to_datetime(df['timestamp'])

            return df
        except (sqlite3.Error, pd.errors.DatabaseError) as e:
            print(f"Error retrieving system history: {e}")
            return pd.DataFrame()

    def get_top_processes_by_cpu(self, limit: int = 5) -> pd.DataFrame:
        if not self.conn:
            self.initialize_database()

        try:
            query = """
            SELECT name, AVG(cpu_percent) as avg_cpu,
                   AVG(memory_mb) as avg_memory,
                   COUNT(*) as count
            FROM process_history
            GROUP BY name
            ORDER BY avg_cpu DESC
            LIMIT ?
            """

            df = pd.read_sql_query(query, self.conn, params=[limit])
            return df
        except (sqlite3.Error, pd.errors.DatabaseError) as e:
            print(f"Error retrieving top processes: {e}")
            return pd.DataFrame()

    def get_process_trend(self, process_name: str) -> pd.DataFrame:
        if not self.conn:
            self.initialize_database()

        try:
            query = """
            SELECT timestamp, cpu_percent, memory_mb
            FROM process_history
            WHERE name = ?
            ORDER BY timestamp
            """

            df = pd.read_sql_query(query, self.conn, params=[process_name])

            df['timestamp'] = pd.to_datetime(df['timestamp'])

            if not df.empty:
                df = df.set_index('timestamp')
                df = df.resample('5T').mean().reset_index()

            return df
        except (sqlite3.Error, pd.errors.DatabaseError) as e:
            print(f"Error retrieving process trend: {e}")
            return pd.DataFrame()

    def cleanup_old_data(self, days: int = 7) -> None:
        if not self.conn:
            self.initialize_database()

        try:
            time_limit = (datetime.now() - pd.Timedelta(days=days)).isoformat()

            cursor = self.conn.cursor()

            cursor.execute(
                "DELETE FROM process_history WHERE timestamp < ?",
                [time_limit]
            )

            cursor.execute(
                "DELETE FROM system_history WHERE timestamp < ?",
                [time_limit]
            )

            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error cleaning up old data: {e}")

    def close(self) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None

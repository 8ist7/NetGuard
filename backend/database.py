import csv
import io
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "database" / "netguard.db"


def connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                severity TEXT NOT NULL DEFAULT 'INFO',
                event_type TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS monitoring_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                local_ip TEXT,
                gateway TEXT,
                dns_server TEXT,
                interface TEXT,
                internet_ok INTEGER,
                dns_ok INTEGER,
                device_count INTEGER,
                open_service_count INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        columns = {row[1] for row in conn.execute("PRAGMA table_info(security_events)").fetchall()}
        if "severity" not in columns:
            conn.execute("ALTER TABLE security_events ADD COLUMN severity TEXT NOT NULL DEFAULT 'INFO'")
        snapshot_columns = {row[1] for row in conn.execute("PRAGMA table_info(monitoring_snapshots)").fetchall()}
        if "open_service_count" not in snapshot_columns:
            conn.execute("ALTER TABLE monitoring_snapshots ADD COLUMN open_service_count INTEGER DEFAULT 0")
        conn.commit()


def add_event(event_type, message, severity="INFO"):
    with connection() as conn:
        conn.execute(
            "INSERT INTO security_events(severity, event_type, message) VALUES (?, ?, ?)",
            (severity.upper(), event_type, message)
        )
        conn.commit()


def get_events(limit=100):
    with connection() as conn:
        rows = conn.execute(
            "SELECT id, severity, event_type, message, created_at FROM security_events ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
    return [dict(row) for row in rows]


def add_snapshot(data):
    with connection() as conn:
        conn.execute("""
            INSERT INTO monitoring_snapshots
            (local_ip, gateway, dns_server, interface, internet_ok, dns_ok, device_count, open_service_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("local_ip"),
            data.get("gateway"),
            data.get("dns_server"),
            data.get("interface"),
            int(bool(data.get("internet"))),
            int(bool(data.get("dns"))),
            data.get("device_count", 0),
            data.get("open_service_count", 0)
        ))
        conn.commit()


def get_snapshots(limit=20):
    with connection() as conn:
        rows = conn.execute(
            "SELECT * FROM monitoring_snapshots ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
    return [dict(row) for row in rows]


def events_csv():
    rows = get_events(1000)
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["Timestamp", "Event Type", "Severity", "Description"],
    )
    writer.writeheader()
    for row in rows:
        writer.writerow({
            "Timestamp": row["created_at"],
            "Event Type": row["event_type"],
            "Severity": row["severity"],
            "Description": row["message"],
        })
    return output.getvalue()

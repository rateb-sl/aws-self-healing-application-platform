#!/usr/bin/env python3
"""Small dependency-free CloudSentinel status service for local development.

The AWS deployment will replace the local SQLite store with RDS-backed storage.
The HTTP contract is intentionally stable so the ALB health check and evidence
workflow can be tested before AWS resources exist.
"""

from __future__ import annotations

import json
import os
import sqlite3
import threading
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse


APP_VERSION = os.getenv("APP_VERSION", "0.1.0-local")
INSTANCE_ID = os.getenv("INSTANCE_ID", "local-instance")
AVAILABILITY_ZONE = os.getenv("AVAILABILITY_ZONE", "local")
DB_PATH = os.getenv("CLOUDSENTINEL_DB", "/tmp/cloudsentinel.sqlite3")


class EventStore:
    """Minimal durable event store used for the local proof and unit tests."""

    def __init__(self, path: str = DB_PATH) -> None:
        self.path = path
        self._lock = threading.Lock()
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS service_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    instance_id TEXT NOT NULL,
                    availability_zone TEXT NOT NULL,
                    application_version TEXT NOT NULL,
                    observed_at TEXT NOT NULL,
                    message TEXT NOT NULL
                )
                """
            )

    def record(self, event_type: str, message: str) -> dict[str, Any]:
        observed_at = datetime.now(timezone.utc).isoformat()
        with self._lock, self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO service_events
                  (event_type, instance_id, availability_zone,
                   application_version, observed_at, message)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    event_type,
                    INSTANCE_ID,
                    AVAILABILITY_ZONE,
                    APP_VERSION,
                    observed_at,
                    message,
                ),
            )
            event_id = cursor.lastrowid
        return self.get(event_id)

    def get(self, event_id: int | None) -> dict[str, Any]:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM service_events WHERE id = ?", (event_id,)
            ).fetchone()
        return dict(row) if row else {}

    def recent(self, limit: int = 10) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM service_events ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(row) for row in rows]


STORE = EventStore()


def payload(status: str = "operational") -> dict[str, Any]:
    return {
        "service": "CloudSentinel",
        "status": status,
        "application_version": APP_VERSION,
        "instance_id": INSTANCE_ID,
        "availability_zone": AVAILABILITY_ZONE,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


def response_json(handler: BaseHTTPRequestHandler, status: int, body: Any) -> None:
    encoded = json.dumps(body, sort_keys=True).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(encoded)))
    handler.end_headers()
    handler.wfile.write(encoded)


class CloudSentinelHandler(BaseHTTPRequestHandler):
    server_version = "CloudSentinel/0.1"

    def log_message(self, format: str, *args: Any) -> None:
        # Keep logs useful while avoiding default noisy reverse-DNS lookups.
        print("%s - %s" % (self.address_string(), format % args))

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        path = urlparse(self.path).path
        if path == "/healthz":
            response_json(self, HTTPStatus.OK, {"status": "ok"})
            return
        if path == "/readyz":
            response_json(self, HTTPStatus.OK, {"status": "ready", **payload()})
            return
        if path == "/api/status":
            response_json(self, HTTPStatus.OK, payload())
            return
        if path == "/api/incidents":
            response_json(self, HTTPStatus.OK, {"events": STORE.recent()})
            return
        if path == "/":
            self._render_status_page()
            return
        response_json(self, HTTPStatus.NOT_FOUND, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        path = urlparse(self.path).path
        if path != "/api/heartbeat":
            response_json(self, HTTPStatus.NOT_FOUND, {"error": "not_found"})
            return
        event = STORE.record("heartbeat", "Application heartbeat received")
        response_json(self, HTTPStatus.CREATED, event)

    def _render_status_page(self) -> None:
        state = payload()
        events = STORE.recent()
        rows = "".join(
            "<li>{event_type} — {instance_id} — {observed_at}</li>".format(**event)
            for event in events
        ) or "<li>No events recorded yet.</li>"
        html = f"""<!doctype html>
<html lang=\"en\">
<head><meta charset=\"utf-8\"><title>CloudSentinel</title></head>
<body>
<h1>CloudSentinel</h1>
<p><strong>Status:</strong> {state['status']}</p>
<ul>
<li><strong>Version:</strong> {state['application_version']}</li>
<li><strong>Instance:</strong> {state['instance_id']}</li>
<li><strong>Zone:</strong> {state['availability_zone']}</li>
</ul>
<h2>Recent service events</h2>
<ul>{rows}</ul>
</body>
</html>""".encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(html)))
        self.end_headers()
        self.wfile.write(html)


def main() -> None:
    host = os.getenv("CLOUDSENTINEL_HOST", "127.0.0.1")
    port = int(os.getenv("CLOUDSENTINEL_PORT", "8080"))
    server = ThreadingHTTPServer((host, port), CloudSentinelHandler)
    print(f"CloudSentinel listening on http://{host}:{port}")
    STORE.record("startup", "CloudSentinel process started")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping CloudSentinel")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()

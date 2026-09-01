import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from .db import get_connection, initialize_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Retry database connection during startup because PostgreSQL
    # may take a few seconds to become ready in Kubernetes.
    for attempt in range(10):
        try:
            initialize_database()
            break
        except Exception:
            if attempt == 9:
                raise
            time.sleep(2)

    yield


app = FastAPI(
    title="SRE Kubernetes System Info",
    lifespan=lifespan,
)


# I completed the assignment.


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SRE Kubernetes System Info</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 40px;
                background: #f5f5f5;
                color: #222;
            }

            h1 {
                margin-bottom: 5px;
            }

            .subtitle {
                color: #666;
                margin-bottom: 25px;
            }

            .cards {
                display: flex;
                flex-wrap: wrap;
                gap: 15px;
                margin-bottom: 25px;
            }

            .card {
                background: white;
                padding: 20px;
                border-radius: 8px;
                min-width: 180px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            }

            .card-title {
                color: #666;
                font-size: 14px;
            }

            .card-value {
                font-size: 24px;
                font-weight: bold;
                margin-top: 8px;
            }

            table {
                width: 100%;
                border-collapse: collapse;
                background: white;
                box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            }

            th, td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }

            th {
                background: #eee;
            }

            .error {
                color: #b00020;
                margin: 15px 0;
            }

            .footer {
                margin-top: 20px;
                color: #777;
                font-size: 13px;
            }
        </style>
    </head>

    <body>
        <h1>SRE Kubernetes System Info</h1>
        <div class="subtitle">
            Kubernetes CronJob monitoring dashboard
        </div>

        <div class="cards">
            <div class="card">
                <div class="card-title">Application Status</div>
                <div class="card-value" id="status">Loading...</div>
            </div>

            <div class="card">
                <div class="card-title">Last Collection</div>
                <div class="card-value" id="lastRun">Loading...</div>
            </div>

            <div class="card">
                <div class="card-title">Records Stored</div>
                <div class="card-value" id="recordCount">0</div>
            </div>
        </div>

        <div id="error" class="error"></div>

        <table>
            <thead>
                <tr>
                    <th>Collected At</th>
                    <th>Hostname</th>
                    <th>CPU Count</th>
                    <th>Memory (MB)</th>
                    <th>Disk Usage (%)</th>
                    <th>Load Average</th>
                </tr>
            </thead>

            <tbody id="systemInfo">
                <tr>
                    <td colspan="6">Loading...</td>
                </tr>
            </tbody>
        </table>

        <div class="footer">
            Dashboard automatically refreshes every 30 seconds.
        </div>

        <script>
            async function loadSystemInfo() {
                try {
                    const response = await fetch("/api/system-info");

                    if (!response.ok) {
                        throw new Error("Unable to retrieve system information");
                    }

                    const data = await response.json();

                    document.getElementById("status").textContent = "Running";
                    document.getElementById("recordCount").textContent = data.length;
                    document.getElementById("error").textContent = "";

                    const tableBody = document.getElementById("systemInfo");

                    if (data.length === 0) {
                        tableBody.innerHTML =
                            '<tr><td colspan="6">No system information collected yet.</td></tr>';

                        document.getElementById("lastRun").textContent = "N/A";
                        return;
                    }

                    const latest = data[0];

                    document.getElementById("lastRun").textContent =
                        new Date(latest.collected_at).toLocaleString();

                    tableBody.innerHTML = data.map(row => `
                        <tr>
                            <td>${new Date(row.collected_at).toLocaleString()}</td>
                            <td>${row.hostname}</td>
                            <td>${row.cpu_count}</td>
                            <td>${row.memory_mb}</td>
                            <td>${row.disk_usage_percent}</td>
                            <td>${row.load_average}</td>
                        </tr>
                    `).join("");

                } catch (error) {
                    document.getElementById("status").textContent = "Unavailable";
                    document.getElementById("error").textContent = error.message;
                }
            }

            loadSystemInfo();

            setInterval(loadSystemInfo, 30000);
        </script>
    </body>
    </html>
    """


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


@app.get("/ready")
def ready():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()

        return {
            "status": "ready",
        }

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database is not available",
        )


@app.get("/api/system-info")
def system_info():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        id,
                        collected_at,
                        hostname,
                        cpu_count,
                        memory_mb,
                        disk_usage_percent,
                        load_average
                    FROM system_info
                    ORDER BY collected_at DESC
                    LIMIT 20
                    """
                )

                rows = cur.fetchall()

        return [
            {
                "id": row[0],
                "collected_at": row[1],
                "hostname": row[2],
                "cpu_count": row[3],
                "memory_mb": row[4],
                "disk_usage_percent": row[5],
                "load_average": row[6],
            }
            for row in rows
        ]

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database is not available",
        )

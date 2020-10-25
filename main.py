from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from collections import namedtuple
import uuid

import sqlite3
from datetime import datetime
import time

Row = namedtuple("Row", "ip count latest first")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

show_rows = True

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    start_time = time.time()
    request_time = str(datetime.now())
    requested_ip = request.client.host

    conn = sqlite3.connect('sqlite.db')
    c = conn.cursor()

    c.execute(f"INSERT INTO log(uuid,ip,timestamp) VALUES ('{uuid.uuid4().hex}','{requested_ip}','{request_time}')")
    conn.commit()

    if (show_rows):
        row_count_cursor = c.execute("""SELECT COUNT(*) FROM log""")
        row_count = row_count_cursor.fetchone()[0]

        res = c.execute("""
            SELECT ip, COUNT(ip) as count, MAX(timestamp) as max_timestamp, MIN(timestamp) as min_timestamp 
            FROM log
            GROUP BY ip
        """)
        rows = [ Row(r[0], r[1], r[2], r[3]) for r in res ]
    else:
        rows = []
        row_count = 0

    conn.close()
    end_time = time.time()

    time_lapsed = "{0:.0f} ms".format((end_time - start_time) * 1000)

    return templates.TemplateResponse("item.html", {
        "request": request, 
        "row_count": row_count, 
        "request_time": request_time,
        "rows": rows,
        "time_lapsed": time_lapsed
    })
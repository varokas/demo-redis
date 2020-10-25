from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from collections import namedtuple
import uuid
import uvicorn

import sqlite3
from datetime import datetime
import time
import redis
import pickle

Cache = namedtuple("Cache", "rows rows_count data_time")
Row = namedtuple("Row", "ip count latest first")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

import argparse

parser = argparse.ArgumentParser(description='Redis Demo')
parser.add_argument('--port', '-p', metavar='port', type=int, default=8080, help='Port')
parser.add_argument('--redis', '-r', action='store_true', default=False)
parser.add_argument('--bglog', action='store_true', default=True)

args = parser.parse_args()

use_redis = args.redis
background_log = args.bglog
lock_expire_ms = 2000
cached_expire_ms = 3000

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request, background_tasks: BackgroundTasks):
    request_time = str(datetime.now())
    requested_ip = request.client.host
    r = redis.Redis(host='localhost', port=6379, db=0)

    # Log current 
    if background_log:
        background_tasks.add_task(log_ip, requested_ip, request_time)
        save_time_lapsed = "N/A - background"
    else:
        conn = sqlite3.connect('sqlite.db')
        c = conn.cursor()
        save_start_time = time.time()
        c.execute(f"INSERT INTO log(uuid,ip,timestamp) VALUES ('{uuid.uuid4().hex}','{requested_ip}','{request_time}')")
        conn.commit()
        conn.close()
        save_time_lapsed = "{0:.0f} ms".format((time.time() - save_start_time) * 1000)

    load_start_time = time.time()
    if use_redis:
        # Check For value in cache
        data_bytes = r.get("data")
        if not data_bytes:
            # Data not in cache, synchronously populates
            populate_data_into_redis()
            data_bytes = r.get("data")

        # Data already in cache
        cached_object = pickle.loads(data_bytes)
        cached_data_time = datetime.fromisoformat(cached_object.data_time)

        if (datetime.now() - cached_data_time).total_seconds() * 1000 > cached_expire_ms:
            print("Cache: Schedule Data Populate")
            # If cached expires, schedule a refresh but use the stale data anyway
            background_tasks.add_task(populate_data_into_redis)

        rows, row_count, data_time = cached_object

    else:
        conn = sqlite3.connect('sqlite.db')
        c = conn.cursor()

        row_count_cursor = c.execute("""SELECT COUNT(*) FROM log""")
        row_count = row_count_cursor.fetchone()[0]

        res = c.execute("""
            SELECT ip, COUNT(ip) as count, MAX(timestamp) as max_timestamp, MIN(timestamp) as min_timestamp 
            FROM log
            GROUP BY ip
        """)
        rows = [ Row(r[0], r[1], r[2], r[3]) for r in res ]
        data_time = str(datetime.now())

        conn.close()

    load_time_lapsed = "{0:.0f} ms".format((time.time() - load_start_time) * 1000)
    

    return templates.TemplateResponse("item.html", {
        "request": request, 
        "row_count": row_count, 
        "request_time": request_time,
        "data_time": data_time,
        "rows": rows,
        "load_time_lapsed": load_time_lapsed,
        "save_time_lapsed": save_time_lapsed
    })

def log_ip(requested_ip, request_time):
    conn = sqlite3.connect('sqlite.db')
    c = conn.cursor()
    save_start_time = time.time()
    c.execute(f"INSERT INTO log(uuid,ip,timestamp) VALUES ('{uuid.uuid4().hex}','{requested_ip}','{request_time}')")
    conn.commit()
    conn.close()
    save_time_lapsed = "{0:.0f} ms".format((time.time() - save_start_time) * 1000)

def populate_data_into_redis():
    conn = sqlite3.connect('sqlite.db')
    c = conn.cursor()
    r = redis.Redis(host='localhost', port=6379, db=0)

    ## Note: This simple Locking algorithm works only for single instance redis
    ##       For a complete distributed implementation -- https://redis.io/topics/distlock
    
    # Acquire Lock so we don't try to repeatedly populate cache
    lock_value = uuid.uuid4().hex
    lock_set = r.set("lock", lock_value, px=lock_expire_ms, nx=True)
    
    # If we successfully obtain the lock
    if lock_set:
        # Load Data
        row_count_cursor = c.execute("""SELECT COUNT(*) FROM log""")
        row_count = row_count_cursor.fetchone()[0]

        res = c.execute("""
            SELECT ip, COUNT(ip) as count, MAX(timestamp) as max_timestamp, MIN(timestamp) as min_timestamp 
            FROM log
            GROUP BY ip
        """)
        rows = [ Row(r[0], r[1], r[2], r[3]) for r in res ]
        data_time = str(datetime.now())

        # Save into cache
        cache_bytes = pickle.dumps(Cache(rows, row_count, data_time))
        r.set("data", cache_bytes)

        print("Cache: Repopulated - " + data_time)

        
        # Remove the lock once done
        if r.get("lock") == lock_value:
            r.delete("lock")
    else:
        # If we cannot obtain a lock, it means some other requests are populating the cache
        # Just use whatever the current value exists in cache
        pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=args.port)
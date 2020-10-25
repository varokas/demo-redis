"""prepopulate log table

Revision ID: 59d8725a08a2
Revises: 0fac98c9ed57
Create Date: 2020-10-17 20:02:55.867790

"""
from alembic import op
import sqlalchemy as sa
import uuid
from datetime import datetime
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer, Date

# revision identifiers, used by Alembic.
revision = '59d8725a08a2'
down_revision = '0fac98c9ed57'
branch_labels = None
depends_on = None
import uuid

log_table = table('log',
    column('uuid', String),
    column('ip', String),
    column('timestamp', String)
)

sample_ips = [
    "5.199.130.188",
    "18.27.197.252",
    "23.106.34.44",
    "23.129.64.188",
    "23.129.64.205",
    "23.160.208.246",
    "23.241.106.252",
    "23.242.241.224",
    "24.27.65.14",
    "124.62.62.102",
    "4.99.187.150"
]

copies = 10000

def upgrade():
    rows = [{"uuid": uuid.uuid4().hex, "ip":ip, "timestamp": str(datetime.now())} for ip in sample_ips * copies]

    op.bulk_insert(log_table, rows)


def downgrade():
    in_clause = ",".join([f"\"{ip}\"" for ip in sample_ips])
    op.execute(f"DELETE FROM log where ip IN ({in_clause})")

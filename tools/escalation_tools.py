from pathlib import Path
import sys
from datetime import datetime

sys.path.append(str(Path(__file__).resolve().parent.parent))

from database.database import get_connection


def create_escalation(customer_id, issue, priority="Medium"):

    connection = get_connection()
    cursor = connection.cursor()

    ticket_id = f"TKT{datetime.now().strftime('%Y%m%d%H%M%S')}"

    cursor.execute("""
        INSERT INTO escalations
        (
            ticket_id,
            customer_id,
            issue,
            priority,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        ticket_id,
        customer_id,
        issue,
        priority,
        "Open",
        datetime.now().isoformat()
    ))

    connection.commit()
    connection.close()

    return {
        "success": True,
        "ticket_id": ticket_id,
        "status": "Open",
        "message": "Your issue has been forwarded to our support team."
    }
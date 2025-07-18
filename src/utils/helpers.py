from datetime import datetime, timedelta
from typing import List, Dict


def is_time_in_slots(requested_time: datetime, slots: List[Dict[str, str]]) -> bool:
    for slot in slots:
        start = datetime.strptime(slot["start"], "%H:%M").time()
        end = datetime.strptime(slot["end"], "%H:%M").time()

        start_time = datetime.combine(requested_time.date(), start)
        end_time = datetime.combine(requested_time.date(), end)

        if end_time <= start_time:
            end_time += timedelta(days=1)

        if start_time <= requested_time <= end_time:
            return True
    return False

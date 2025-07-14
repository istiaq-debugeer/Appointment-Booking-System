from datetime import datetime
from typing import List, Dict

def is_time_in_slots(appointment_time: datetime, slots: List[Dict[str, str]]) -> bool:
    """
    Checks if the given appointment time falls into any of the doctor's available time slots.
    Assumes time format is HH:MM and same day.
    """
    appointment_str = appointment_time.strftime("%H:%M")
    
    for slot in slots:
        start = slot["start"]
        end = slot["end"]

        if start <= appointment_str <= end:
            return True
    
    return False
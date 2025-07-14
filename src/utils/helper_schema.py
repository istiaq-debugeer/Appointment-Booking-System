from pydantic import BaseModel
from typing import List
from datetime import datetime

class TimeSlot(BaseModel):
    start: str  # "10:00"
    end: str    # "11:00"

class DoctorWithSlots(BaseModel):
    id: int
    full_name: str
    available_timeslots: List[TimeSlot] = []
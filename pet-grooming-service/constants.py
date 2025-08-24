from enum import Enum


class LeadStatus(str, Enum):
    INITIATED = "initiated"
    QUALIFIED = "qualified"
    BOOKED = "booked"

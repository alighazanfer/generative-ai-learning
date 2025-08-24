import uuid
import datetime
from models import GlobalState
from constants import LeadStatus
from google_sheet import append_row
from chains import QUALIFY_LEAD_CHAIN


def initiate_lead(state: GlobalState):
    lead_id = "LEAD" + uuid.uuid4().hex[:6].upper()
    created_at = datetime.now().isoformat()

    new_row = [
        lead_id,
        created_at,
        "",
        "",
        "",
        "",
        "",
        LeadStatus.INITIATED,
    ]

    append_row(sheet_name="Leads__preview_", new_row=new_row)
    return state


def qualify_lead(state: GlobalState):
    result = QUALIFY_LEAD_CHAIN.invoke({"query": state.query})
    print(result)

    # Update status to LeadStatus.QUALIFIED
    return state

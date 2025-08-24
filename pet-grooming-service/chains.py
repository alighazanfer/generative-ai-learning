from config import model
from models import QualifyLead
from prompts import qualify_lead_prompt

qualify_lead_structured_model = model.with_structured_output(QualifyLead)

QUALIFY_LEAD_CHAIN = qualify_lead_prompt | qualify_lead_structured_model

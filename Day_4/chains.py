from models import model
from schemas import RouterDecision, DesignationInfo
from prompts import llm_router_prompt, designation_info_prompt


llm_router_structured_model = model.with_structured_output(RouterDecision)
designation_info_structured_model = model.with_structured_output(DesignationInfo)


LLM_ROUTER_CHAIN = llm_router_prompt | llm_router_structured_model
DESIGNATION_INFO_CHAIN = designation_info_prompt | designation_info_structured_model

from pydantic import BaseModel, Field
from typing import List, Optional

class ScientificObjective(BaseModel):
    id: str
    code: str
    title: str
    category: str
    description: str
    scientific_rationale: str
    primary_instruments: List[str]
    target_formations: List[str]
    recommended_checkpoint_ids: List[str]
    biosignature_relevance: str

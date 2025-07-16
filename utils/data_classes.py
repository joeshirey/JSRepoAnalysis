from dataclasses import dataclass, field
from typing import Dict, Any, List
from datetime import datetime


@dataclass
class AnalysisResult:
    """
    A data class to hold the results of a file analysis.
    """

    git_info: Dict[str, Any]
    region_tags: List[str]
    evaluation_data: Dict[str, Any]
    raw_code: str
    evaluation_date: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M")
    )

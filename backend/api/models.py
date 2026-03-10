from pydantic import BaseModel
from typing import List, Optional

class AnalyzeRequest(BaseModel):
    repo_url: str
    github_token: Optional[str] = None

class DependencyInfo(BaseModel):
    name: str
    current_version: str
    latest_version: Optional[str] = None
    is_outdated: bool = False
    file_path: str

class UpgradePlanItem(BaseModel):
    dependency: str
    from_version: str
    to_version: str
    breaking_changes: str
    risk_level: str
    recommended: bool
    reasoning: str

class AnalyzeResponse(BaseModel):
    repo_url: str
    dependencies: List[DependencyInfo]
    upgrade_plan: List[UpgradePlanItem]

class UpgradeRequest(BaseModel):
    repo_url: str
    plan: List[UpgradePlanItem]
    github_token: str

class UpgradeResponse(BaseModel):
    success: bool
    pr_url: Optional[str] = None
    message: str

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import dotenv

dotenv.load_dotenv(override=True)
from api.models import AnalyzeRequest, AnalyzeResponse, UpgradeRequest, UpgradeResponse
from core.repo_analyzer import analyze_repo
from ai.planner import generate_upgrade_plan
from core.github_upgrader import apply_upgrades_and_create_pr

app = FastAPI(title="PatchPilot API", description="Automated dependency upgrades using AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to PatchPilot API"}

@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze_repository(request: AnalyzeRequest):
    try:
        # 1. Clone & Analyze Repo
        dependencies = analyze_repo(request.repo_url, request.github_token)
        
        # 2. Get Upgrade Plan
        upgrade_plan = generate_upgrade_plan(dependencies)
        
        return AnalyzeResponse(
            repo_url=request.repo_url,
            dependencies=dependencies,
            upgrade_plan=upgrade_plan
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upgrade", response_model=UpgradeResponse)
def upgrade_repository(request: UpgradeRequest):
    if not request.github_token:
        raise HTTPException(status_code=400, detail="GitHub token is required to create a Pull Request.")
        
    try:
        print(f"Applying upgrade plan to {request.repo_url}")
        
        # 1. Execute Upgrade & Create PR
        pr_url = apply_upgrades_and_create_pr(
            repo_url=request.repo_url,
            plan=request.plan,
            github_token=request.github_token
        )
        
        if not pr_url:
            return UpgradeResponse(
                success=False,
                pr_url=None,
                message="No files were locally modified. They may already be up to date."
            )
            
        return UpgradeResponse(
            success=True,
            pr_url=pr_url,
            message="Successfully upgraded dependencies and created a GitHub Pull Request!"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create PR: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

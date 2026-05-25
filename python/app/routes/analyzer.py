from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.responses import HTMLResponse

from app.services.clone_repo import clone_repo
from app.services.report import build_report
from app.analyzers import controler
from app.testCoverage import testCoverage

router = APIRouter()


class RepoRequest(BaseModel):
    url: str


@router.post("/analyze")
def analyze_repo(data: RepoRequest):

    repo = clone_repo(data.url)
   
    result1 = controler.run(repo)
    result3 = testCoverage.run(repo)

    return {
        "message": "Repo clonado com sucesso",
        "path": repo["repo_path"], 
        "result1": result1,
        "result3": result3,
    }

@router.post("/report")
def generate_report(data: dict):
    html = build_report(data)
    return HTMLResponse(content=html)
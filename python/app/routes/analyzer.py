from fastapi import APIRouter
from pydantic import BaseModel

from app.services.clone_repo import clone_repo

router = APIRouter()


class RepoRequest(BaseModel):
    url: str


@router.post("/analyze")
def analyze_repo(data: RepoRequest):

    repo = clone_repo(data.url)

    return {
        "message": "Repo clonado com sucesso",
        "path": repo["repo_path"]
    }
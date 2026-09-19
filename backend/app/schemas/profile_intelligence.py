from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, model_validator


class JobMatchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    job_id: UUID | None = None
    job_description: str | None = Field(default=None, min_length=20, max_length=20000)
    required_skills: list[str] = Field(default_factory=list, max_length=80)

    @model_validator(mode="after")
    def valid_target(self):
        if bool(self.job_id) == bool(self.job_description):
            raise ValueError("Select a job OR paste a job description.")
        if self.job_id and self.required_skills:
            raise ValueError("Saved jobs use their own required skills.")
        if any(not name.strip() or len(name) > 150 for name in self.required_skills):
            raise ValueError("Each required skill must contain 1 to 150 characters.")
        return self


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class ProfileChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    question: str = Field(min_length=1, max_length=4000)
    provider: Literal["openai", "claude", "gemini"] = "gemini"
    compare: bool = False
    scope: Literal["profile", "resume", "project", "documents", "job"] = "profile"
    project_id: UUID | None = None
    document_id: UUID | None = None
    target: JobMatchRequest | None = None
    version: str | None = Field(default=None, max_length=64)
    conversation_history: list[ChatTurn] = Field(default_factory=list, max_length=10)

    @model_validator(mode="after")
    def valid_scope(self):
        if self.project_id and self.scope != "project":
            raise ValueError("Project selection requires project scope.")
        if self.document_id and self.scope not in {"project", "documents"}:
            raise ValueError("Document selection requires project or document scope.")
        if self.target and self.scope != "job":
            raise ValueError("Job requirements require job scope.")
        if self.scope == "project" and not self.project_id:
            raise ValueError("Choose a project.")
        if self.scope == "job" and not self.target:
            raise ValueError("Choose a target job or paste its description.")
        return self

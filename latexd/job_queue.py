"""Async job queue for tracking compilation requests."""

import uuid
import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


@dataclass
class Job:
    job_id: str
    snippet: str
    fmt: str
    status: JobStatus = JobStatus.PENDING
    result: Optional[bytes] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "status": self.status.value,
            "fmt": self.fmt,
            "error": self.error,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class JobQueue:
    def __init__(self) -> None:
        self._jobs: Dict[str, Job] = {}

    def create(self, snippet: str, fmt: str) -> Job:
        job_id = str(uuid.uuid4())
        job = Job(job_id=job_id, snippet=snippet, fmt=fmt)
        self._jobs[job_id] = job
        return job

    def get(self, job_id: str) -> Optional[Job]:
        return self._jobs.get(job_id)

    def update(self, job_id: str, status: JobStatus,
               result: Optional[bytes] = None,
               error: Optional[str] = None) -> None:
        job = self._jobs.get(job_id)
        if job is None:
            raise KeyError(f"Job {job_id!r} not found")
        job.status = status
        job.result = result
        job.error = error
        job.updated_at = time.time()

    def all_jobs(self) -> list:
        return [j.to_dict() for j in self._jobs.values()]

    def clear(self) -> int:
        count = len(self._jobs)
        self._jobs.clear()
        return count


_queue = JobQueue()


def get_queue() -> JobQueue:
    return _queue

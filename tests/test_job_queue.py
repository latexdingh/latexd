"""Unit tests for the JobQueue class."""

import time
import pytest
from latexd.job_queue import JobQueue, JobStatus


@pytest.fixture
def queue():
    return JobQueue()


def test_create_job_returns_pending(queue):
    job = queue.create("x^2", "svg")
    assert job.status == JobStatus.PENDING
    assert job.snippet == "x^2"
    assert job.fmt == "svg"
    assert job.job_id


def test_get_existing_job(queue):
    job = queue.create("y", "png")
    fetched = queue.get(job.job_id)
    assert fetched is job


def test_get_missing_job_returns_none(queue):
    assert queue.get("nonexistent-id") is None


def test_update_job_status(queue):
    job = queue.create("z", "svg")
    queue.update(job.job_id, JobStatus.RUNNING)
    assert queue.get(job.job_id).status == JobStatus.RUNNING


def test_update_job_done_with_result(queue):
    job = queue.create("a", "svg")
    queue.update(job.job_id, JobStatus.DONE, result=b"<svg/>")
    fetched = queue.get(job.job_id)
    assert fetched.status == JobStatus.DONE
    assert fetched.result == b"<svg/>"
    assert fetched.error is None


def test_update_job_failed_with_error(queue):
    job = queue.create("b", "png")
    queue.update(job.job_id, JobStatus.FAILED, error="compile error")
    fetched = queue.get(job.job_id)
    assert fetched.status == JobStatus.FAILED
    assert fetched.error == "compile error"


def test_update_unknown_job_raises(queue):
    with pytest.raises(KeyError):
        queue.update("bad-id", JobStatus.DONE)


def test_all_jobs_returns_dicts(queue):
    queue.create("c", "svg")
    queue.create("d", "png")
    jobs = queue.all_jobs()
    assert len(jobs) == 2
    assert all(isinstance(j, dict) for j in jobs)


def test_clear_removes_all(queue):
    queue.create("e", "svg")
    queue.create("f", "png")
    count = queue.clear()
    assert count == 2
    assert queue.all_jobs() == []


def test_to_dict_has_expected_keys(queue):
    job = queue.create("g", "svg")
    d = job.to_dict()
    for key in ("job_id", "status", "fmt", "error", "created_at", "updated_at"):
        assert key in d


def test_updated_at_changes_on_update(queue):
    job = queue.create("h", "svg")
    original_ts = job.updated_at
    time.sleep(0.01)
    queue.update(job.job_id, JobStatus.RUNNING)
    assert queue.get(job.job_id).updated_at > original_ts


def test_create_job_ids_are_unique(queue):
    """Each created job should receive a distinct job_id."""
    ids = {queue.create("x", "svg").job_id for _ in range(10)}
    assert len(ids) == 10


def test_all_jobs_reflects_status_updates(queue):
    """all_jobs() should return the current state after a status update."""
    job = queue.create("i", "svg")
    queue.update(job.job_id, JobStatus.DONE, result=b"<svg/>")
    jobs_by_id = {j["job_id"]: j for j in queue.all_jobs()}
    assert jobs_by_id[job.job_id]["status"] == JobStatus.DONE.value

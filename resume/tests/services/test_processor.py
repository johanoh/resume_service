import pytest

from core.exceptions import BusinessError
from resume.models import Resume
from resume.services.processor import process


def test_create_resumes_ok():
    # given
    external_id = "resume_1"
    work_experiences = ["Software Engineer at XYZ"]
    skills = ["Python", "Django"]

    raw_resume = {
        "id": external_id,
        "work_experiences": work_experiences,
        "skills": skills,
    }

    # when
    resume = process(raw_resume=raw_resume, sleep_time=0)

    # then
    assert isinstance(resume, Resume)
    assert resume.external_id == external_id
    assert resume.skills == skills
    assert resume.work_experiences == work_experiences


def test_create_resume_fail():
    # given
    external_id = "resume_1"
    work_experiences = []
    skills = ["Python", "Django"]

    raw_resume = {
        "id": external_id,
        "work_experiences": work_experiences,
        "skills": skills,
    }

    # when/then
    with pytest.raises(BusinessError):
        process(raw_resume=raw_resume, sleep_time=0)

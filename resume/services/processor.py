from typing import List
import time

from core.exceptions import BusinessError

from resume.framework import Response
from resume.models import Resume


def process(raw_resume: dict, raw_data_id: int, sleep_time: int = 2) -> Resume:
    time.sleep(sleep_time)  # simulate parsing
    resume = Response(raw_resume.get('id'), raw_resume.get('skills'), raw_resume.get('work_experiences'))
    if not resume.valid:
        raise BusinessError(f"unable to process resume {resume.id}")
    return Resume(
        external_id=resume.id,
        skills=resume.skills,
        work_experiences=resume.work_experiences,
        raw_data_id=raw_data_id
    )

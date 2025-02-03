from typing import List
import logging

from celery import shared_task

logger = logging.getLogger(__name__)

from core.exceptions import BusinessError

from data_collection.models import RawData, Statuses

from resume.models import Resume
from resume.services.processor import process


@shared_task
def process_resumes(raw_data_id: int, batch_size: int = 1, sleep_time: int = 2):
    raw_data = RawData.objects.get(id=raw_data_id)
    batches = [raw_data.parsed_data[i:i + batch_size] for i in range(0, len(raw_data.parsed_data), batch_size)]
    for batch in batches:
        batch_process_resumes.apply_async(
            kwargs={
                'raw_resumes': batch,
                'raw_data_id': raw_data.id,
                'sleep_time': sleep_time
            }
        )



@shared_task
def batch_process_resumes(raw_resumes: list, raw_data_id: int, sleep_time: int = 2):

    raw_data = RawData.objects.get(id=raw_data_id)
    resumes: List[Resume] = []
    for raw_resume in raw_resumes:
        try:
            resumes.append(process(raw_resume=raw_resume, raw_data_id=raw_data_id, sleep_time=sleep_time))
        except BusinessError as e:
            logger.error(e)
            raw_data.status = Statuses.ERROR

    if resumes:
        Resume.objects.bulk_create(
            resumes,
            update_conflicts=True,
            unique_fields=['external_id'],
            update_fields=['skills', 'work_experiences']
        )

        if raw_data.status != Statuses.ERROR:
            raw_data.status = Statuses.PROCESSED
        raw_data.save()


    


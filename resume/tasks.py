from typing import List
import logging

from celery import shared_task

logger = logging.getLogger(__name__)

from core.exceptions import BusinessError

from data_collection.models import RawData, Statuses, DataRequest

from resume.models import Resume
from resume.services.processor import process


@shared_task
def process_resumes(raw_data_id: int, batch_size: int = 1, sleep_time: int = 2):
    raw_data = RawData.objects.get(id=raw_data_id)
    data_request = raw_data.data_request
    if data_request.status != Statuses.PROCESSING:
        data_request.status = Statuses.PROCESSING
        data_request.save()

    batches = [
        raw_data.parsed_data[i : i + batch_size]
        for i in range(0, len(raw_data.parsed_data), batch_size)
    ]
    for batch in batches:
        batch_process_resumes.apply_async(
            kwargs={
                "raw_resumes": batch,
                "raw_data_id": raw_data.id,
                "sleep_time": sleep_time,
            }
        )


@shared_task
def batch_process_resumes(raw_resumes: list, raw_data_id: int, sleep_time: int = 2):
    raw_data = RawData.objects.get(id=raw_data_id)
    raw_data.status = Statuses.PROCESSING
    raw_data.save()
    resumes: List[Resume] = []
    for raw_resume in raw_resumes:
        try:
            resumes.append(
                process(
                    raw_resume=raw_resume,
                    raw_data_id=raw_data_id,
                    sleep_time=sleep_time,
                )
            )
        except BusinessError as e:
            logger.error(e)
            raw_data.status = Statuses.ERROR

    if resumes:
        Resume.objects.bulk_create(
            resumes,
            update_conflicts=True,
            unique_fields=["external_id"],
            update_fields=["skills", "work_experiences"],
        )

        if raw_data.status != Statuses.ERROR:
            raw_data.status = Statuses.COMPLETED
        raw_data.save()

    data_request = raw_data.data_request
    if (
        data_request.raw_data.filter(status=Statuses.ERROR).distinct("status").exists()
    ):  # check statuses of all raw data and set the data request to the right status, #this can be improved
        data_request.status = Statuses.ERROR
        data_request.save()
        return

    if data_request.raw_data.filter(status=Statuses.COMPLETED).count() == data_request.raw_data.count():
        data_request.status = Statuses.COMPLETED
        data_request.save()
        return
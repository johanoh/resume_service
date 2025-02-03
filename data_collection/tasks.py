import time
import random
import requests
import json
import logging

from celery import shared_task
from celery.exceptions import MaxRetriesExceededError

from resume.tasks import process_resumes
from data_collection.models import RawData, DataRequest

logger = logging.getLogger(__name__)


@shared_task
def trigger_data_pull(
    count=100, per_page=10, batch_size: int = 10, error_mode: bool = False
):
    data_request = DataRequest.objects.create()
    fetch_resumes_from_mock_api.apply_async(
        kwargs={
            "data_request_id": data_request.id,
            "count": count,
            "per_page": per_page,
            "batch_size": batch_size,
            "page": 1,
            "error_mode": error_mode,
        }
    )


@shared_task(
    rate_limit="30/s",  # respect API rate limit, limit 429s
    autoretry_for=(requests.RequestException,),
    retry_backoff=2,
    retry_jitter=True,
    max_retries=5,
)
def fetch_resumes_from_mock_api(
    data_request_id: int,
    count: int = 100,
    per_page: int = 10,
    page: int = 1,
    batch_size=10,
    error_mode: bool = False,
    next_url=None,
):
    try:
        if next_url:
            next_url.replace("localhost", "web")
        url = (
            next_url
            or f"http://web:8000/api/v1/test-data?count={count}&per_page={per_page}&page={page}&errors={error_mode}"
        )  # ran into docker networking issue, easier to use container name

        response = requests.get(url)
        api_latency = random.uniform(0.05, 0.2)
        time.sleep(api_latency)  # Simulating network latency

        if response.status_code == 429:  # retry if we get rate limited anywys
            retry_after = int(response.headers.get("Retry-After", 1))
            logger.warning(f"Rate limited! Retrying in {retry_after} seconds...")
            raise fetch_resumes_from_mock_api.retry(countdown=retry_after)

        response.raise_for_status()

        data = response.json()
        resumes = data.get("results", [])
        next_page_url = data.get("next", None)

        # write raw data to DB
        RawData.objects.create(
            data_format=RawData.DataFormats.JSON,
            data_type=RawData.DataTypes.RESUME,
            raw_data=json.dumps(resumes) if resumes else [],
            data_request_id=data_request_id,
        )

        if next_page_url:  # recursively access the API
            fetch_resumes_from_mock_api.apply_async(
                kwargs={
                    "data_request_id": data_request_id,
                    "count": count,
                    "per_page": per_page,
                    "batch_size": batch_size,
                    "next_url": next_page_url,
                }
            )
        else:
            logger.info(
                f"All pages fetched for DataRequest {data_request_id}. Starting processing."
            )
            raw_datum = RawData.objects.filter(data_request_id=data_request_id)
            for raw_data in raw_datum:
                process_resumes.apply_async(
                    kwargs={"raw_data_id": raw_data.id, "batch_size": batch_size}
                )

    except MaxRetriesExceededError:
        logger.error(f"Max retries reached for page {page}. Skipping.")
    except requests.RequestException as e:
        logger.error(f"Failed to fetch page {page}: {e}")

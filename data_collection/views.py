from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from data_collection.tasks import trigger_data_pull
import logging

logger = logging.getLogger(__name__)

class TriggerDataPullAPI(APIView):

    def post(self, request):
        count = int(request.data.get("count", 100))
        per_page = int(request.data.get("per_page", 10))
        batch_size = int(request.data.get("batch_size", 10))

        # Trigger Celery task
        trigger_data_pull.apply_async(kwargs={
            "count": count,
            "per_page": per_page,
            "batch_size": batch_size
        })

        logger.info(f"Triggered data pull: count={count}, per_page={per_page}, batch_size={batch_size}")

        return Response(
            {"message": f"Data collection started: count {count}, per_page {per_page}, batch_size {batch_size}"},
            status=status.HTTP_202_ACCEPTED
        )

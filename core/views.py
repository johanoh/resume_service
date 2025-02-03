from typing import List
import random
import logging

from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from uuid import uuid4

logger = logging.getLogger(__name__)

MOCK_SKILLS = ["Python", "Django", "Flask", "SQL", "AWS", "React", "Docker", "NOSQL", "Node"]
MOCK_WORK_EXPERIENCES = [
    "Software Engineer at XYZ",
    "Backend Developer at ABC",
    "Data Scientist at AI Labs",
    "DevOps Engineer at CloudCorp",
    "Frontend Developer at QQQ"
]

def generate_mock_resume(error: bool = False) -> dict:
    if error:
        return {
            "id": str(uuid4()),
            "skills": [],
            "work_experiences": [],
            "error": "Invalid resume data",
        }
    
    return {
        "id": str(uuid4()),
        "skills": random.sample(MOCK_SKILLS, random.randint(1, 3)),
        "work_experiences": random.sample(MOCK_WORK_EXPERIENCES, random.randint(1, 4))
    }

class MockResumePagination(PageNumberPagination):  # custom mock pagination
    page_size_query_param = "per_page"
    page_size = 10

class MockResumeAPI(APIView, MockResumePagination):
    """
    Mock API that returns fake resume data for testing.
    Supports pagination and error simulation.
    """

    throttle_classes = [ScopedRateThrottle]  # Rate limit set in settings.py (30/sec)
    throttle_scope = "test_data"

    def get(self, request):
        user_ip = request.META.get("REMOTE_ADDR", "Unknown IP")
        logger.info(f"API Accessed: {request.path} from {user_ip}")
        count = int(request.GET.get("count", 50)) 
        error_mode = request.GET.get("errors", "false").lower() == "true"

        sample_resumes: List[dict] = [generate_mock_resume() for _ in range(count)]
        if error_mode:
            sample_resumes[-1] = generate_mock_resume(error=True)

        paginated_data = self.paginate_queryset(sample_resumes, request, view=self)
        return self.get_paginated_response(paginated_data)

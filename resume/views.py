from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, CharFilter
from resume.models import Resume
from django.db.models import Q
from resume.serializers import ResumeSerializer


class ResumeFilter(FilterSet):
    skills = CharFilter(method="filter_skills")

    def filter_skills(
        self, queryset, name, value
    ):  # name required because of django_filters
        match_type = self.request.GET.get("match", "any")  # Default to OR
        skills_list = value.split(",")

        query_filter = Q()
        for skill in skills_list:
            if match_type == "all":  # AND search
                query_filter &= Q(skills__icontains=skill)
            else:  # OR search (default)
                query_filter |= Q(skills__icontains=skill)

        return queryset.filter(query_filter)

    class Meta:
        model = Resume
        fields = ["skills"]


class ResumeListAPI(ListAPIView):
    queryset = Resume.objects.all().order_by("-created_at")
    serializer_class = ResumeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ResumeFilter
    search_fields = ["skills"]

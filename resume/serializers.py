from rest_framework import serializers
from resume.models import Resume


class ResumeSerializer(serializers.ModelSerializer):
    skills = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = Resume
        fields = ["id", "skills", "created_at"]

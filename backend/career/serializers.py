
from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import (
    Profile,
    Job,
    Resume,
    Application,
    InterviewAttempt
)

User = get_user_model()


# -----------------------------
# User Registration
# -----------------------------
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "password",
            "role",
            "company_name"
        )

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)

        Profile.objects.create(
            user=user,
            full_name=user.username,
            skills=[]
        )

        return user

    def validate_role(self, value):
        if value not in ("CANDIDATE", "RECRUITER"):
            raise serializers.ValidationError(
                "Choose Candidate or Recruiter."
            )
        return value


# -----------------------------
# User Details
# -----------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "role",
            "company_name"
        )


# -----------------------------
# Candidate Profile
# -----------------------------
class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = (
            "user",
            "full_name",
            "headline",
            "location",
            "phone",
            "bio",
            "skills",
            "experience_years",
            "updated_at"
        )


# -----------------------------
# Job Details
# -----------------------------
class JobSerializer(serializers.ModelSerializer):
    recruiter_name = serializers.CharField(
        source="recruiter.username",
        read_only=True
    )

    application_count = serializers.IntegerField(
        source="applications.count",
        read_only=True
    )

    is_applied = serializers.SerializerMethodField()

    def get_is_applied(self, obj):
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            return False

        if request.user.role != "CANDIDATE":
            return False

        return Application.objects.filter(
            job=obj,
            candidate=request.user
        ).exists()

    class Meta:
        model = Job
        fields = "__all__"
        read_only_fields = (
            "recruiter",
            "created_at"
        )


# -----------------------------
# Resume Details
# -----------------------------
class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = (
            "id",
            "file",
            "original_name",
            "extracted_skills",
            "created_at"
        )

        read_only_fields = (
            "extracted_skills",
            "created_at"
        )


# -----------------------------
# Job Application
# -----------------------------
class ApplicationSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(
        source="job.title",
        read_only=True
    )

    company = serializers.CharField(
        source="job.company",
        read_only=True
    )

    candidate_email = serializers.CharField(
        source="candidate.email",
        read_only=True
    )

    class Meta:
        model = Application
        fields = (
            "id",
            "candidate",
            "candidate_email",
            "job",
            "job_title",
            "company",
            "resume",
            "status",
            "cover_note",
            "created_at"
        )

        read_only_fields = (
            "candidate",
            "status",
            "created_at"
        )


# -----------------------------
# Interview Practice
# -----------------------------
class InterviewAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewAttempt

        fields = (
            "id",
            "role",
            "level",
            "question",
            "answer",
            "score",
            "feedback",
            "created_at"
        )

        read_only_fields = (
            "score",
            "feedback",
            "created_at"
        )

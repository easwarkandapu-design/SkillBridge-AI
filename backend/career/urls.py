from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView, MeView, ProfileView, JobListCreateView, JobDetailView, ApplyView,
    ApplicationListView, ApplicationStatusView, ResumeUploadView, ResumeListView,
    ResumeAnalysisView, RecommendationsView, QuestionsView, EvaluateView, DashboardView
)

urlpatterns = [
    path("auth/register/", RegisterView.as_view()),
    path("auth/login/", TokenObtainPairView.as_view()),
    path("auth/token/refresh/", TokenRefreshView.as_view()),
    path("auth/me/", MeView.as_view()),
    path("profile/", ProfileView.as_view()),
    path("jobs/", JobListCreateView.as_view()),
    path("jobs/<int:pk>/", JobDetailView.as_view()),
    path("jobs/<int:pk>/apply/", ApplyView.as_view()),
    path("applications/", ApplicationListView.as_view()),
    path("applications/<int:pk>/status/", ApplicationStatusView.as_view()),
    path("resumes/upload/", ResumeUploadView.as_view()),
    path("resumes/", ResumeListView.as_view()),
    path("resumes/<int:pk>/analysis/", ResumeAnalysisView.as_view()),
    path("matching/recommendations/", RecommendationsView.as_view()),
    path("interviews/questions/", QuestionsView.as_view()),
    path("interviews/evaluate/", EvaluateView.as_view()),
    path("dashboard/", DashboardView.as_view()),
]

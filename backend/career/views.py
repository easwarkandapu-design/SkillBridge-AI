from pathlib import Path
from django.db.models import Q
from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Profile, Job, Resume, Application, InterviewAttempt
from .serializers import RegisterSerializer, UserSerializer, ProfileSerializer, JobSerializer, ResumeSerializer, ApplicationSerializer, InterviewAttemptSerializer
from .ai_services import extract_resume_text, extract_skills, calculate_match, QUESTION_BANK, evaluate_answer
from .permissions import IsRecruiterOrReadOnly

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class MeView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response(UserSerializer(request.user).data)

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile

class JobListCreateView(generics.ListCreateAPIView):
    serializer_class = JobSerializer
    permission_classes = [IsRecruiterOrReadOnly]
    def get_queryset(self):
        qs = Job.objects.filter(is_active=True).select_related("recruiter")
        search = self.request.query_params.get("search")
        location = self.request.query_params.get("location")
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search) | Q(company__icontains=search))
        if location:
            qs = qs.filter(location__icontains=location)
        return qs
    def perform_create(self, serializer):
        serializer.save(recruiter=self.request.user, company=serializer.validated_data.get("company") or self.request.user.company_name or self.request.user.username)

class JobDetailView(generics.RetrieveUpdateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]
    def update(self, request, *args, **kwargs):
        job = self.get_object()
        if job.recruiter_id != request.user.id and request.user.role != "ADMIN":
            return Response({"detail": "You cannot edit this job."}, status=403)
        return super().update(request, *args, **kwargs)

class ApplyView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, pk):
        if request.user.role != "CANDIDATE":
            return Response({"detail": "Only candidates can apply."}, status=403)
        try:
            job = Job.objects.get(pk=pk, is_active=True)
        except Job.DoesNotExist:
            return Response({"detail": "Job not found."}, status=404)
        app, created = Application.objects.get_or_create(candidate=request.user, job=job, defaults={"cover_note": request.data.get("cover_note", "")})
        if not created:
            return Response({"detail": "You have already applied to this job."}, status=400)
        return Response(ApplicationSerializer(app).data, status=201)

class ApplicationListView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        if user.role == "RECRUITER":
            return Application.objects.filter(job__recruiter=user).select_related("candidate", "job")
        return Application.objects.filter(candidate=user).select_related("candidate", "job")

class ApplicationStatusView(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, pk):
        try:
            app = Application.objects.select_related("job").get(pk=pk)
        except Application.DoesNotExist:
            return Response({"detail": "Application not found."}, status=404)
        if request.user.role not in ("RECRUITER", "ADMIN") or (app.job.recruiter_id != request.user.id and request.user.role != "ADMIN"):
            return Response({"detail": "Not allowed."}, status=403)
        allowed = [x[0] for x in Application.Status.choices]
        new_status = request.data.get("status")
        if new_status not in allowed:
            return Response({"detail": "Invalid status."}, status=400)
        app.status = new_status
        app.save(update_fields=["status"])
        return Response(ApplicationSerializer(app).data)

class ResumeUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    def post(self, request):
        uploaded = request.FILES.get("file")
        if not uploaded:
            return Response({"detail": "Choose a PDF or DOCX file."}, status=400)
        suffix = Path(uploaded.name).suffix.lower()
        if suffix not in (".pdf", ".docx"):
            return Response({"detail": "Only PDF and DOCX files are supported."}, status=400)
        if uploaded.size > 5 * 1024 * 1024:
            return Response({"detail": "Maximum file size is 5 MB."}, status=400)
        resume = Resume(user=request.user, file=uploaded, original_name=Path(uploaded.name).name)
        resume.save()
        try:
            text = extract_resume_text(resume.file.path)
            skills = extract_skills(text)
            resume.extracted_text = text[:50000]
            resume.extracted_skills = skills
            resume.save(update_fields=["extracted_text", "extracted_skills"])
        except Exception as exc:
            resume.delete()
            return Response({"detail": f"Could not read this document: {str(exc)}"}, status=400)
        profile, _ = Profile.objects.get_or_create(user=request.user)
        profile.skills = sorted(set(profile.skills + skills))
        profile.save(update_fields=["skills", "updated_at"])
        return Response(ResumeSerializer(resume).data, status=201)

class ResumeListView(generics.ListAPIView):
    serializer_class = ResumeSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user).order_by("-created_at")

class ResumeAnalysisView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        try:
            resume = Resume.objects.get(pk=pk, user=request.user)
        except Resume.DoesNotExist:
            return Response({"detail": "Resume not found."}, status=404)
        return Response({
            "id": resume.id, "filename": resume.original_name,
            "skills": resume.extracted_skills,
            "word_count": len(resume.extracted_text.split()),
            "summary": "Skills detected from the uploaded document. Review the extracted data for accuracy.",
            "suggestions": ["Tailor your summary to each job description.", "Add measurable outcomes to project and experience bullets.", "Include relevant skills only when you genuinely have them."]
        })

class RecommendationsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        resume = Resume.objects.filter(user=request.user).order_by("-created_at").first()
        skills = set(profile.skills or [])
        if resume:
            skills.update(resume.extracted_skills or [])
        results = []
        for job in Job.objects.filter(is_active=True):
            result = calculate_match(list(skills), job.skills, profile.experience_years, job.experience_years)
            results.append({"job": JobSerializer(job).data, **result})
        return Response(sorted(results, key=lambda x: x["score"], reverse=True))

class QuestionsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        role = request.query_params.get("role", "frontend developer").lower()
        level = request.query_params.get("level", "Intermediate")
        questions = []
        for role_key, levels in QUESTION_BANK.items():
            if role_key in role or role in role_key:
                questions = levels.get(level, levels.get("Intermediate", []))
                break
        if not questions:
            questions = QUESTION_BANK["full stack developer"].get(level, QUESTION_BANK["full stack developer"]["Intermediate"])
        return Response([{"question": q, "category": role.title()} for q, _ in questions])

class EvaluateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        role = request.data.get("role", "Full Stack Developer")
        level = request.data.get("level", "Intermediate")
        question = request.data.get("question", "")
        answer = request.data.get("answer", "")
        if not question or not answer.strip():
            return Response({"detail": "Question and answer are required."}, status=400)
        score, feedback = evaluate_answer(role, question, answer)
        attempt = InterviewAttempt.objects.create(user=request.user, role=role, level=level, question=question, answer=answer, score=score, feedback=feedback)
        return Response(InterviewAttemptSerializer(attempt).data, status=201)

class DashboardView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        if user.role == "RECRUITER":
            jobs = Job.objects.filter(recruiter=user)
            apps = Application.objects.filter(job__recruiter=user)
            return Response({"role": user.role, "jobs_count": jobs.count(), "applications_count": apps.count(),
                             "shortlisted_count": apps.filter(status="SHORTLISTED").count(),
                             "recent_applications": ApplicationSerializer(apps[:5], many=True).data})
        apps = Application.objects.filter(candidate=user)
        profile, _ = Profile.objects.get_or_create(user=user)
        return Response({"role": user.role, "applications_count": apps.count(),
                         "interviews_count": InterviewAttempt.objects.filter(user=user).count(),
                         "resume_count": Resume.objects.filter(user=user).count(),
                         "skills_count": len(profile.skills or []),
                         "recent_applications": ApplicationSerializer(apps[:5], many=True).data})

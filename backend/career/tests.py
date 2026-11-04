from django.test import TestCase
from .ai_services import calculate_match, extract_skills

class MatchingTests(TestCase):
    def test_match_explains_missing_skills(self):
        result = calculate_match(["Python", "Django"], ["Python", "Django", "PostgreSQL"])
        self.assertEqual(result["matched_skills"], ["django", "python"])
        self.assertEqual(result["missing_skills"], ["postgresql"])
        self.assertGreater(result["score"], 0)

    def test_skill_extraction(self):
        skills = extract_skills("I build apps with Python, Django and PostgreSQL.")
        self.assertIn("Python", skills)
        self.assertIn("Django", skills)

from django.test import TestCase
from django.urls import reverse

from .models import AssessmentResponse
from .risk_engine import analyze_assessment


class RiskEngineTests(TestCase):
    def setUp(self):
        self.low_readiness = AssessmentResponse.objects.create(
            location_type='coastal',
            household_size=7,
            housing_type='kutcha',
            has_emergency_kit=False,
            has_water_storage=False,
            has_first_aid_knowledge=False,
            past_disaster_experience=False,
            self_rated_preparedness=1,
            has_evacuation_plan=False,
            knows_emergency_contacts=False,
        )
        self.high_readiness = AssessmentResponse.objects.create(
            location_type='coastal',
            household_size=3,
            housing_type='pucca',
            has_emergency_kit=True,
            has_water_storage=True,
            has_first_aid_knowledge=True,
            past_disaster_experience=True,
            self_rated_preparedness=5,
            has_evacuation_plan=True,
            knows_emergency_contacts=True,
        )

    def test_model_uses_shared_engine_for_preparedness_score(self):
        expected_score = self.high_readiness.calculate_preparedness_score()
        self.assertEqual(self.high_readiness.preparedness_score, expected_score)
        self.assertEqual(self.high_readiness.preparedness_level, 'high')
        self.assertEqual(self.low_readiness.preparedness_level, 'low')

    def test_disaster_scores_change_with_response_quality(self):
        low_analysis = analyze_assessment(self.low_readiness)
        high_analysis = analyze_assessment(self.high_readiness)

        low_scores = {item['key']: item['score'] for item in low_analysis['disasters']}
        high_scores = {item['key']: item['score'] for item in high_analysis['disasters']}

        self.assertGreater(high_scores['flood'], low_scores['flood'])
        self.assertGreater(high_scores['cyclone'], low_scores['cyclone'])
        self.assertGreater(high_scores['fire'], low_scores['fire'])
        self.assertGreater(high_scores['pandemic'], low_scores['pandemic'])

    def test_risk_analysis_view_renders_dynamic_content(self):
        response = self.client.get(reverse('risk_analysis'), {'response_id': self.high_readiness.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Preparedness Capability Radar')
        self.assertContains(response, 'Why this score was assigned')
        self.assertContains(response, 'Personalized actions')
        self.assertContains(response, 'Flood')
        self.assertContains(response, 'Cyclone')
        self.assertContains(response, 'data-progress')

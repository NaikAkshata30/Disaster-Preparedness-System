from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .risk_engine import calculate_overall_preparedness_score, score_to_preparedness_level


class AssessmentResponse(models.Model):
    """Model to store disaster preparedness assessment responses."""

    LOCATION_CHOICES = [
        ('urban', 'Urban Area'),
        ('rural', 'Rural Area'),
        ('coastal', 'Coastal Area'),
        ('hilly', 'Hilly/Mountainous Area'),
    ]

    HOUSING_CHOICES = [
        ('pucca', 'Pucca (Concrete/Brick)'),
        ('semi_pucca', 'Semi-Pucca'),
        ('kutcha', 'Kutcha (Mud/Temporary)'),
        ('apartment', 'Apartment/Flat'),
    ]

    PREPAREDNESS_LEVEL_CHOICES = [
        ('low', 'Low Preparedness'),
        ('medium', 'Medium Preparedness'),
        ('high', 'High Preparedness'),
    ]

    location_type = models.CharField(max_length=20, choices=LOCATION_CHOICES)
    household_size = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(50)])
    housing_type = models.CharField(max_length=20, choices=HOUSING_CHOICES)
    has_emergency_kit = models.BooleanField(default=False)
    has_water_storage = models.BooleanField(default=False)
    has_first_aid_knowledge = models.BooleanField(default=False)
    past_disaster_experience = models.BooleanField(default=False)
    self_rated_preparedness = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    has_evacuation_plan = models.BooleanField(default=False)
    knows_emergency_contacts = models.BooleanField(default=False)

    preparedness_score = models.FloatField(default=0.0)
    preparedness_level = models.CharField(max_length=10, choices=PREPAREDNESS_LEVEL_CHOICES, default='low')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def calculate_preparedness_score(self):
        """Calculate preparedness score using the shared assessment engine."""
        return calculate_overall_preparedness_score(self)

    def determine_preparedness_level(self):
        """Classify preparedness level using the shared thresholds."""
        return score_to_preparedness_level(self.preparedness_score)

    def save(self, *args, **kwargs):
        """Auto-calculate score and level before saving."""
        self.preparedness_score = self.calculate_preparedness_score()
        self.preparedness_level = self.determine_preparedness_level()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Assessment #{self.id} - {self.preparedness_level} ({self.preparedness_score})"

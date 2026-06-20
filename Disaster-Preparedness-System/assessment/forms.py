from django import forms
from .models import AssessmentResponse


class PreparednessAssessmentForm(forms.ModelForm):
    """Form for disaster preparedness assessment"""
    
    class Meta:
        model = AssessmentResponse
        fields = [
            'location_type', 'household_size', 'housing_type',
            'has_emergency_kit', 'has_water_storage', 'has_first_aid_knowledge',
            'past_disaster_experience', 'self_rated_preparedness',
            'has_evacuation_plan', 'knows_emergency_contacts',
        ]
        
        widgets = {
            'location_type': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'household_size': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '50', 'required': True}),
            'housing_type': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'has_emergency_kit': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_water_storage': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_first_aid_knowledge': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'past_disaster_experience': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'self_rated_preparedness': forms.Select(choices=[(i, i) for i in range(1, 6)], attrs={'class': 'form-select', 'required': True}),
            'has_evacuation_plan': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'knows_emergency_contacts': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
        labels = {
            'location_type': '📍 Location Type',
            'household_size': '👨‍👩‍👧‍👦 Household Size',
            'housing_type': '🏠 Housing Type',
            'has_emergency_kit': '🎒 Emergency Kit Available',
            'has_water_storage': '💧 Water Storage Available',
            'has_first_aid_knowledge': '⚕️ First-Aid Knowledge',
            'past_disaster_experience': '⚠️ Past Disaster Experience',
            'self_rated_preparedness': '⭐ Self-Rated Preparedness Level',
            'has_evacuation_plan': '🚪 Family Evacuation Plan',
            'knows_emergency_contacts': '📞 Know Emergency Contacts',
        }
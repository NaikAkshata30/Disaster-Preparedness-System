from __future__ import annotations

from copy import deepcopy
from typing import Dict, List, Tuple


# Central configuration for all preparedness logic.
# Keeping the rules here avoids scattering hardcoded values across models/views/templates.
DISASTER_CONFIGS = {
    'earthquake': {
        'name': 'Earthquake',
        'icon': '🏚️',
        'location_scores': {'urban': 6, 'rural': 4, 'coastal': 3, 'hilly': 12},
        'housing_scores': {'pucca': 10, 'semi_pucca': 2, 'kutcha': -10, 'apartment': 6},
        'boolean_factors': {
            'has_emergency_kit': {
                'label': 'Emergency kit available',
                'positive': 14,
                'negative': -14,
                'recommendation': 'Prepare a grab-and-go emergency kit with torch, food, documents, and basic tools.',
            },
            'has_water_storage': {
                'label': 'Water storage available',
                'positive': 8,
                'negative': -8,
                'recommendation': 'Store at least three days of safe drinking water for every household member.',
            },
            'has_evacuation_plan': {
                'label': 'Family evacuation plan',
                'positive': 16,
                'negative': -16,
                'recommendation': 'Create a family evacuation and reunification plan with a safe open meeting point.',
            },
            'has_first_aid_knowledge': {
                'label': 'First-aid knowledge',
                'positive': 14,
                'negative': -12,
                'recommendation': 'Learn basic first aid and injury response for collapse, cuts, and fractures.',
            },
            'knows_emergency_contacts': {
                'label': 'Emergency contacts known',
                'positive': 10,
                'negative': -10,
                'recommendation': 'Keep emergency service numbers and family contact details accessible offline.',
            },
            'past_disaster_experience': {
                'label': 'Awareness training / past experience',
                'positive': 8,
                'negative': -4,
                'recommendation': 'Join local earthquake drills or awareness sessions to practice response steps.',
            },
        },
    },
    'flood': {
        'name': 'Flood',
        'icon': '🌊',
        'location_scores': {'urban': 6, 'rural': 10, 'coastal': 16, 'hilly': 4},
        'housing_scores': {'pucca': 6, 'semi_pucca': 0, 'kutcha': -10, 'apartment': 8},
        'boolean_factors': {
            'has_emergency_kit': {
                'label': 'Emergency kit available',
                'positive': 12,
                'negative': -12,
                'recommendation': 'Keep a flood-ready emergency kit packed in waterproof bags or containers.',
            },
            'has_water_storage': {
                'label': 'Water storage available',
                'positive': 16,
                'negative': -12,
                'recommendation': 'Protect clean water supplies because floodwater often contaminates local sources.',
            },
            'has_evacuation_plan': {
                'label': 'Family evacuation plan',
                'positive': 18,
                'negative': -18,
                'recommendation': 'Map the fastest route to higher ground and practice evacuation with the family.',
            },
            'has_first_aid_knowledge': {
                'label': 'First-aid knowledge',
                'positive': 10,
                'negative': -10,
                'recommendation': 'Learn first aid for drowning, cuts, infections, and water-related emergencies.',
            },
            'knows_emergency_contacts': {
                'label': 'Emergency contacts known',
                'positive': 10,
                'negative': -8,
                'recommendation': 'Save helpline, shelter, and local rescue contact numbers before the rainy season.',
            },
            'past_disaster_experience': {
                'label': 'Awareness training / past experience',
                'positive': 10,
                'negative': -4,
                'recommendation': 'Participate in flood awareness programs to understand warning signs and response timing.',
            },
        },
    },
    'cyclone': {
        'name': 'Cyclone',
        'icon': '🌀',
        'location_scores': {'urban': 7, 'rural': 8, 'coastal': 18, 'hilly': 4},
        'housing_scores': {'pucca': 8, 'semi_pucca': 1, 'kutcha': -12, 'apartment': 6},
        'boolean_factors': {
            'has_emergency_kit': {
                'label': 'Emergency kit available',
                'positive': 12,
                'negative': -12,
                'recommendation': 'Maintain a cyclone kit with light, radio, medicines, batteries, and dry food.',
            },
            'has_water_storage': {
                'label': 'Water storage available',
                'positive': 10,
                'negative': -8,
                'recommendation': 'Store sealed drinking water in case supply lines fail during severe storms.',
            },
            'has_evacuation_plan': {
                'label': 'Family evacuation plan',
                'positive': 18,
                'negative': -18,
                'recommendation': 'Identify the nearest cyclone shelter and prepare a timed evacuation plan.',
            },
            'has_first_aid_knowledge': {
                'label': 'First-aid knowledge',
                'positive': 10,
                'negative': -10,
                'recommendation': 'Train for injury response related to debris, falls, and storm aftermath.',
            },
            'knows_emergency_contacts': {
                'label': 'Emergency contacts known',
                'positive': 12,
                'negative': -10,
                'recommendation': 'Keep local weather alert, shelter, and emergency contact numbers ready.',
            },
            'past_disaster_experience': {
                'label': 'Awareness training / past experience',
                'positive': 10,
                'negative': -4,
                'recommendation': 'Review cyclone warning signals and participate in seasonal preparedness drills.',
            },
        },
    },
    'fire': {
        'name': 'Fire',
        'icon': '🔥',
        'location_scores': {'urban': 14, 'rural': 6, 'coastal': 5, 'hilly': 5},
        'housing_scores': {'pucca': 8, 'semi_pucca': 2, 'kutcha': -12, 'apartment': 10},
        'boolean_factors': {
            'has_emergency_kit': {
                'label': 'Emergency kit available',
                'positive': 10,
                'negative': -12,
                'recommendation': 'Add a fire-ready go-bag and keep essential items easy to grab during evacuation.',
            },
            'has_water_storage': {
                'label': 'Water storage available',
                'positive': 8,
                'negative': -6,
                'recommendation': 'Keep water or other basic suppression resources accessible for early response.',
            },
            'has_evacuation_plan': {
                'label': 'Family evacuation plan',
                'positive': 16,
                'negative': -16,
                'recommendation': 'Practice home fire exits, especially from bedrooms and upper floors.',
            },
            'has_first_aid_knowledge': {
                'label': 'First-aid knowledge',
                'positive': 16,
                'negative': -12,
                'recommendation': 'Learn basic burn care, smoke exposure response, and safe evacuation behaviour.',
            },
            'knows_emergency_contacts': {
                'label': 'Emergency contacts known',
                'positive': 8,
                'negative': -8,
                'recommendation': 'Keep fire service and local emergency numbers posted in visible places.',
            },
            'past_disaster_experience': {
                'label': 'Awareness training / past experience',
                'positive': 8,
                'negative': -4,
                'recommendation': 'Take part in fire safety drills and learn how to respond to alarms quickly.',
            },
        },
    },
    'pandemic': {
        'name': 'Pandemic',
        'icon': '🦠',
        'location_scores': {'urban': 10, 'rural': 6, 'coastal': 6, 'hilly': 5},
        'housing_scores': {'pucca': 4, 'semi_pucca': 2, 'kutcha': -4, 'apartment': 3},
        'boolean_factors': {
            'has_emergency_kit': {
                'label': 'Medical and emergency supplies',
                'positive': 10,
                'negative': -10,
                'recommendation': 'Maintain medical supplies, hygiene items, masks, and essential household stock.',
            },
            'has_water_storage': {
                'label': 'Water and essentials backup',
                'positive': 14,
                'negative': -10,
                'recommendation': 'Keep backup water and basic supplies to reduce urgent trips during outbreaks.',
            },
            'has_evacuation_plan': {
                'label': 'Family continuity plan',
                'positive': 10,
                'negative': -10,
                'recommendation': 'Prepare a family communication and care plan for illness, quarantine, or service disruption.',
            },
            'has_first_aid_knowledge': {
                'label': 'First-aid knowledge',
                'positive': 18,
                'negative': -14,
                'recommendation': 'Build medical readiness through first aid and basic home-care knowledge.',
            },
            'knows_emergency_contacts': {
                'label': 'Emergency contacts known',
                'positive': 18,
                'negative': -14,
                'recommendation': 'Keep hospital, doctor, pharmacy, and family emergency contact numbers organized.',
            },
            'past_disaster_experience': {
                'label': 'Awareness training / past experience',
                'positive': 12,
                'negative': -4,
                'recommendation': 'Follow public-health guidance and join community awareness sessions when available.',
            },
        },
    },
}

RISK_LEVELS = {
    'low': {'label': 'Low Risk', 'class': 'success', 'description': 'Preparedness is strong for this scenario.'},
    'medium': {'label': 'Medium Risk', 'class': 'warning', 'description': 'Preparedness is moderate, but important gaps remain.'},
    'high': {'label': 'High Risk', 'class': 'danger', 'description': 'Preparedness is weak and should be improved urgently.'},
}


def clamp_score(score: float) -> float:
    return round(max(0.0, min(100.0, score)), 1)


def household_factor(response, disaster_key: str) -> Dict[str, object]:
    """Return a family-size modifier. Large households need stronger planning and supplies."""
    size = response.household_size

    if disaster_key == 'pandemic':
        if size <= 2:
            impact = 4
            detail = 'Small household is easier to isolate and coordinate during outbreaks'
        elif size <= 4:
            impact = -2
            detail = 'Medium household requires some extra coordination during health emergencies'
        elif size <= 6:
            impact = -6
            detail = 'Larger household increases care, medicine, and coordination needs during outbreaks'
        else:
            impact = -12
            detail = 'Very large household makes infection control and continuity planning more difficult'
    else:
        if size >= 7 and response.has_evacuation_plan:
            impact = 4
            detail = 'Large household offset by having a family evacuation plan'
        elif size >= 7:
            impact = -10
            detail = 'Large household without a strong family plan is harder to move and coordinate'
        elif size >= 5 and response.has_evacuation_plan:
            impact = 3
            detail = 'Mid-sized household benefits from having an evacuation plan'
        elif size >= 5:
            impact = -5
            detail = 'Mid-sized household needs clearer coordination and supply planning'
        else:
            impact = 2
            detail = 'Smaller household is easier to coordinate during emergencies'

    return {
        'label': f'Household size ({size} members)',
        'impact': impact,
        'detail': detail,
    }


def self_rating_factor(response) -> Dict[str, object]:
    rating_map = {1: -10, 2: -5, 3: 0, 4: 5, 5: 10}
    rating = int(response.self_rated_preparedness)
    impact = rating_map.get(rating, 0)
    return {
        'label': f'Self-rated preparedness ({rating}/5)',
        'impact': impact,
        'detail': 'Self-confidence in readiness influences likely response speed and confidence during a crisis.',
    }


def location_factor(response, config: Dict[str, object]) -> Dict[str, object]:
    impact = config['location_scores'].get(response.location_type, 0)
    detail = f"Location context: {response.get_location_type_display()} changes how relevant this disaster is for the household."
    return {
        'label': response.get_location_type_display(),
        'impact': impact,
        'detail': detail,
    }


def housing_factor(response, config: Dict[str, object]) -> Dict[str, object]:
    impact = config['housing_scores'].get(response.housing_type, 0)
    detail = f"Housing context: {response.get_housing_type_display()} affects resilience and response options."
    return {
        'label': response.get_housing_type_display(),
        'impact': impact,
        'detail': detail,
    }


def boolean_factor(response, field_name: str, factor_config: Dict[str, object]) -> Dict[str, object]:
    has_capability = bool(getattr(response, field_name))
    impact = factor_config['positive'] if has_capability else factor_config['negative']
    return {
        'label': factor_config['label'],
        'impact': impact,
        'detail': factor_config['label'],
        'missing': not has_capability,
        'recommendation': factor_config['recommendation'],
    }


def score_to_risk(score: float) -> Dict[str, str]:
    if score >= 75:
        return deepcopy(RISK_LEVELS['low'])
    if score >= 50:
        return deepcopy(RISK_LEVELS['medium'])
    return deepcopy(RISK_LEVELS['high'])


def score_to_preparedness_level(score: float) -> str:
    if score >= 75:
        return 'high'
    if score >= 50:
        return 'medium'
    return 'low'


def score_label_class(score: float) -> str:
    if score >= 75:
        return 'success'
    if score >= 50:
        return 'warning'
    return 'danger'


def capability_score(points: List[int], bonus: int = 0) -> float:
    raw = bonus + sum(points)
    maximum = bonus + (len(points) * 100 if points else 100)
    if maximum <= 0:
        return 0.0
    return clamp_score((raw / maximum) * 100)


def build_radar_data(response) -> Dict[str, object]:
    emergency_supplies = capability_score([
        100 if response.has_emergency_kit else 35,
        100 if response.has_water_storage else 30,
        90 if response.household_size <= 4 else 70,
    ])
    communication = capability_score([
        100 if response.knows_emergency_contacts else 25,
        100 if response.has_evacuation_plan else 35,
        int((response.self_rated_preparedness / 5) * 100),
    ])
    medical_readiness = capability_score([
        100 if response.has_first_aid_knowledge else 20,
        100 if response.has_emergency_kit else 40,
        100 if response.has_water_storage else 35,
    ])
    evacuation_planning = capability_score([
        100 if response.has_evacuation_plan else 15,
        100 if response.knows_emergency_contacts else 30,
        95 if response.household_size <= 4 else 65,
    ])
    training_awareness = capability_score([
        100 if response.has_first_aid_knowledge else 20,
        100 if response.past_disaster_experience else 35,
        int((response.self_rated_preparedness / 5) * 100),
    ])
    resource_availability = capability_score([
        100 if response.has_emergency_kit else 25,
        100 if response.has_water_storage else 25,
        {'pucca': 95, 'apartment': 88, 'semi_pucca': 70, 'kutcha': 40}.get(response.housing_type, 60),
    ])

    categories = [
        'Emergency Supplies',
        'Communication',
        'Medical Readiness',
        'Evacuation Planning',
        'Training & Awareness',
        'Resource Availability',
    ]
    values = [
        emergency_supplies,
        communication,
        medical_readiness,
        evacuation_planning,
        training_awareness,
        resource_availability,
    ]

    strongest_index = max(range(len(values)), key=lambda index: values[index])
    weakest_index = min(range(len(values)), key=lambda index: values[index])

    return {
        'categories': categories,
        'values': values,
        'strongest': {'name': categories[strongest_index], 'score': values[strongest_index]},
        'weakest': {'name': categories[weakest_index], 'score': values[weakest_index]},
    }


def build_disaster_recommendations(disaster_key: str, response, factors: List[Dict[str, object]]) -> List[str]:
    recommendations: List[str] = []

    for factor in factors:
        if factor.get('missing') and factor.get('recommendation'):
            recommendations.append(factor['recommendation'])

    if disaster_key == 'flood' and response.location_type == 'coastal':
        recommendations.append('Store essential supplies in waterproof containers and identify the quickest route to higher ground.')
    if disaster_key == 'cyclone' and response.location_type == 'coastal':
        recommendations.append('Monitor cyclone alerts closely and keep a shelter movement checklist ready during warning periods.')
    if disaster_key == 'earthquake' and response.location_type == 'hilly':
        recommendations.append('Identify safe open spaces away from slopes, retaining walls, and unstable structures.')
    if disaster_key == 'fire' and response.location_type == 'urban':
        recommendations.append('Install smoke detectors and make sure everyone knows the nearest building exit or stairwell route.')
    if disaster_key == 'pandemic' and response.household_size >= 5:
        recommendations.append('Prepare a family contact tree, medicine checklist, and caregiving plan for sick household members.')
    if disaster_key == 'fire' and response.housing_type == 'apartment':
        recommendations.append('Review apartment fire exits, stairwell access, and assembly points instead of relying on lifts.')
    if disaster_key in {'flood', 'cyclone'} and response.housing_type == 'kutcha':
        recommendations.append('Plan an early relocation option because lighter housing types are more vulnerable in severe weather.')

    deduped: List[str] = []
    seen = set()
    for item in recommendations:
        if item not in seen:
            deduped.append(item)
            seen.add(item)

    if not deduped:
        deduped.append('Maintain your current preparedness actions and review this plan regularly to keep readiness high.')

    return deduped[:4]


def build_disaster_analysis(response) -> List[Dict[str, object]]:
    disaster_analysis: List[Dict[str, object]] = []

    for disaster_key, config in DISASTER_CONFIGS.items():
        factors: List[Dict[str, object]] = [
            location_factor(response, config),
            housing_factor(response, config),
        ]

        for field_name, factor_config in config['boolean_factors'].items():
            factors.append(boolean_factor(response, field_name, factor_config))

        factors.append(self_rating_factor(response))
        factors.append(household_factor(response, disaster_key))

        raw_score = 35 + sum(factor['impact'] for factor in factors)
        preparedness_score = clamp_score(raw_score)
        risk = score_to_risk(preparedness_score)

        formatted_factors = []
        for factor in factors:
            impact = int(factor['impact']) if float(factor['impact']).is_integer() else round(factor['impact'], 1)
            formatted_factors.append(
                {
                    'label': factor['label'],
                    'impact': impact,
                    'impact_label': f"{impact:+}",
                    'impact_class': 'success' if impact >= 0 else 'danger',
                    'status_icon': '✓' if impact >= 0 else '✗',
                    'detail': factor.get('detail', ''),
                }
            )

        disaster_analysis.append(
            {
                'key': disaster_key,
                'name': config['name'],
                'icon': config['icon'],
                'score': preparedness_score,
                'risk_level': risk['label'],
                'risk_class': risk['class'],
                'risk_description': risk['description'],
                'factors': formatted_factors,
                'recommendations': build_disaster_recommendations(disaster_key, response, factors),
                'priority_action': build_disaster_recommendations(disaster_key, response, factors)[0],
            }
        )

    return disaster_analysis


def calculate_overall_preparedness_score(response) -> float:
    radar = build_radar_data(response)
    radar_average = sum(radar['values']) / len(radar['values'])
    discipline_bonus = 0
    for field_name in [
        'has_emergency_kit',
        'has_water_storage',
        'has_first_aid_knowledge',
        'has_evacuation_plan',
        'knows_emergency_contacts',
    ]:
        if getattr(response, field_name):
            discipline_bonus += 2
    if response.past_disaster_experience:
        discipline_bonus += 2

    return clamp_score((radar_average * 0.88) + discipline_bonus)


def build_priority_actions(disaster_analysis: List[Dict[str, object]]) -> List[Dict[str, str]]:
    ordered = sorted(disaster_analysis, key=lambda item: item['score'])
    actions = []
    seen = set()
    for item in ordered:
        recommendation = item['priority_action']
        if recommendation in seen:
            continue
        actions.append({'disaster': item['name'], 'icon': item['icon'], 'action': recommendation})
        seen.add(recommendation)
        if len(actions) == 5:
            break
    return actions


def analyze_assessment(response) -> Dict[str, object]:
    radar = build_radar_data(response)
    disasters = build_disaster_analysis(response)
    overall_score = calculate_overall_preparedness_score(response)
    overall_level = score_to_preparedness_level(overall_score)
    highest_risk = min(disasters, key=lambda item: item['score'])
    strongest_disaster = max(disasters, key=lambda item: item['score'])

    return {
        'overall_score': overall_score,
        'overall_level': overall_level,
        'overall_class': score_label_class(overall_score),
        'radar': radar,
        'disasters': disasters,
        'highest_risk': highest_risk,
        'strongest_disaster': strongest_disaster,
        'priority_actions': build_priority_actions(disasters),
    }

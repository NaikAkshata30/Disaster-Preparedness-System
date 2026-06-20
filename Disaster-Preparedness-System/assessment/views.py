from datetime import datetime

from django.contrib import messages
from django.db.models import Avg, Count
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PreparednessAssessmentForm
from .models import AssessmentResponse
from .risk_engine import analyze_assessment


LEVEL_COLORS = {
    'low': '#dc3545',
    'medium': '#f59f00',
    'high': '#2f9e44',
}

FAMILY_SIZE_OPTIONS = [
    ('1-2', '1-2 Members'),
    ('3-4', '3-4 Members'),
    ('5-6', '5-6 Members'),
    ('7+', '7+ Members'),
]

READINESS_METRICS = [
    ('has_emergency_kit', 'Emergency Kit'),
    ('has_water_storage', 'Water Storage'),
    ('has_first_aid_knowledge', 'First Aid'),
    ('past_disaster_experience', 'Experience'),
    ('has_evacuation_plan', 'Evacuation Plan'),
    ('knows_emergency_contacts', 'Emergency Contacts'),
    ('self_rated_preparedness', 'Self Rating'),
]


def home(request):
    """Home page with disaster awareness."""
    context = {
        'disasters': [
            {
                'name': 'Earthquake',
                'icon': '🏚️',
                'description': 'Sudden ground shaking caused by tectonic plate movements.',
                'preparedness_tips': ['Secure heavy furniture', 'Create evacuation plan', 'Keep emergency kit ready'],
            },
            {
                'name': 'Flood',
                'icon': '🌊',
                'description': 'Overflow of water submerging land.',
                'preparedness_tips': ['Store documents in waterproof containers', 'Know evacuation routes', 'Keep life jackets'],
            },
            {
                'name': 'Cyclone',
                'icon': '🌀',
                'description': 'Violent rotating storms with strong winds.',
                'preparedness_tips': ['Secure loose objects', 'Board up windows', 'Stock emergency supplies'],
            },
            {
                'name': 'Fire',
                'icon': '🔥',
                'description': 'Uncontrolled burning that destroys property.',
                'preparedness_tips': ['Install smoke detectors', 'Keep fire extinguishers', 'Plan escape routes'],
            },
            {
                'name': 'Pandemic',
                'icon': '🦠',
                'description': 'Widespread infectious disease outbreak.',
                'preparedness_tips': ['Maintain hygiene', 'Stock medicines', 'Follow health guidelines'],
            },
        ]
    }
    return render(request, 'assessment/home.html', context)


def assessment(request):
    """Assessment form page."""
    if request.method == 'POST':
        form = PreparednessAssessmentForm(request.POST)
        if form.is_valid():
            response = form.save()
            messages.success(request, f'Assessment completed! Your score is {response.preparedness_score}/100')
            return redirect('results', response_id=response.id)
        messages.error(request, 'Please correct the errors below.')
    else:
        form = PreparednessAssessmentForm()

    return render(request, 'assessment/assessment.html', {'form': form})


def results(request, response_id):
    """Display assessment results."""
    response = get_object_or_404(AssessmentResponse, id=response_id)

    if response.preparedness_level == 'low':
        feedback = {
            'class': 'danger',
            'icon': '❌',
            'title': 'Low Preparedness',
            'message': 'Immediate action required!',
            'priority': 'HIGH',
        }
    elif response.preparedness_level == 'medium':
        feedback = {
            'class': 'warning',
            'icon': '⚠️',
            'title': 'Medium Preparedness',
            'message': 'Good start, but improvement needed.',
            'priority': 'MEDIUM',
        }
    else:
        feedback = {
            'class': 'success',
            'icon': '✅',
            'title': 'High Preparedness',
            'message': 'Excellent! Well prepared.',
            'priority': 'LOW',
        }

    gaps = []
    if not response.has_emergency_kit:
        gaps.append('Emergency Kit')
    if not response.has_water_storage:
        gaps.append('Water Storage')
    if not response.has_first_aid_knowledge:
        gaps.append('First-Aid Knowledge')

    return render(
        request,
        'assessment/results.html',
        {'response': response, 'feedback': feedback, 'gaps': gaps},
    )


def dashboard(request):
    """Interactive analytics dashboard page."""
    return render(
        request,
        'assessment/dashboard.html',
        {
            'no_data': not AssessmentResponse.objects.exists(),
            'preparedness_levels': [
                {'value': value, 'label': label}
                for value, label in AssessmentResponse.PREPAREDNESS_LEVEL_CHOICES
            ],
            'location_types': [
                {'value': value, 'label': label}
                for value, label in AssessmentResponse.LOCATION_CHOICES
            ],
            'family_size_options': [
                {'value': value, 'label': label}
                for value, label in FAMILY_SIZE_OPTIONS
            ],
        },
    )


def dashboard_data(request):
    """Return live dashboard metrics and chart data from database records."""
    payload = build_dashboard_payload(request.GET)
    return JsonResponse(payload)


def dashboard_drilldown(request):
    """Return detailed drill-down data for clicked chart segments."""
    chart = request.GET.get('chart', '')
    payload = build_drilldown_payload(chart, request.GET)
    return JsonResponse(payload)


def get_filtered_queryset(params, exclude_keys=None, overrides=None):
    """Apply dashboard filters to the assessment queryset."""
    exclude_keys = set(exclude_keys or [])
    overrides = overrides or {}

    qs = AssessmentResponse.objects.all()

    start_date = overrides.get('start_date', params.get('start_date'))
    end_date = overrides.get('end_date', params.get('end_date'))
    preparedness_level = overrides.get('preparedness_level', params.get('preparedness_level'))
    location_type = overrides.get('location_type', params.get('location_type'))
    family_size = overrides.get('family_size', params.get('family_size'))

    if 'start_date' not in exclude_keys and start_date:
        qs = qs.filter(created_at__date__gte=start_date)
    if 'end_date' not in exclude_keys and end_date:
        qs = qs.filter(created_at__date__lte=end_date)
    if 'preparedness_level' not in exclude_keys and preparedness_level:
        qs = qs.filter(preparedness_level=preparedness_level)
    if 'location_type' not in exclude_keys and location_type:
        qs = qs.filter(location_type=location_type)
    if 'family_size' not in exclude_keys and family_size:
        qs = apply_family_size_filter(qs, family_size)

    return qs.order_by('-created_at')


def apply_family_size_filter(queryset, family_size):
    """Apply household-size filter bands."""
    if family_size == '1-2':
        return queryset.filter(household_size__gte=1, household_size__lte=2)
    if family_size == '3-4':
        return queryset.filter(household_size__gte=3, household_size__lte=4)
    if family_size == '5-6':
        return queryset.filter(household_size__gte=5, household_size__lte=6)
    if family_size == '7+':
        return queryset.filter(household_size__gte=7)
    return queryset


def family_size_band(size):
    """Convert numeric household size into dashboard filter band."""
    if size <= 2:
        return '1-2'
    if size <= 4:
        return '3-4'
    if size <= 6:
        return '5-6'
    return '7+'


def build_dashboard_payload(params):
    """Build the complete interactive dashboard payload."""
    qs = get_filtered_queryset(params)
    total = qs.count()

    if total == 0:
        return {
            'has_data': False,
            'kpis': {
                'total_assessments': 0,
                'average_score': 0,
                'high_risk_users': 0,
                'prepared_users': 0,
            },
            'charts': {},
            'summary': {
                'filters_applied': summarize_filters(params),
                'last_updated': None,
            },
        }

    average_score = round(qs.aggregate(avg=Avg('preparedness_score'))['avg'] or 0, 1)
    latest_record = qs.first()

    payload = {
        'has_data': True,
        'kpis': {
            'total_assessments': total,
            'average_score': average_score,
            'high_risk_users': qs.filter(preparedness_level='low').count(),
            'prepared_users': qs.filter(preparedness_level='high').count(),
        },
        'charts': {
            'preparedness_bar': build_preparedness_bar_data(qs),
            'location_pie': build_location_pie_data(qs),
            'emergency_kit_donut': build_emergency_kit_donut_data(qs),
            'trend_line': build_trend_line_data(qs),
            'category_comparison': build_category_comparison_data(qs),
            'preparedness_radar': build_preparedness_radar_data(qs),
            'score_heatmap': build_score_heatmap_data(qs),
        },
        'summary': {
            'filters_applied': summarize_filters(params),
            'last_updated': latest_record.updated_at.strftime('%Y-%m-%d %H:%M:%S') if latest_record else None,
        },
    }
    return payload


def summarize_filters(params):
    """Build a human-readable list of active filters."""
    summary = []
    preparedness_level = params.get('preparedness_level')
    location_type = params.get('location_type')
    family_size = params.get('family_size')
    start_date = params.get('start_date')
    end_date = params.get('end_date')

    if preparedness_level:
        summary.append(next((label for value, label in AssessmentResponse.PREPAREDNESS_LEVEL_CHOICES if value == preparedness_level), preparedness_level))
    if location_type:
        summary.append(next((label for value, label in AssessmentResponse.LOCATION_CHOICES if value == location_type), location_type))
    if family_size:
        summary.append(next((label for value, label in FAMILY_SIZE_OPTIONS if value == family_size), family_size))
    if start_date or end_date:
        summary.append(f"{start_date or 'Start'} → {end_date or 'Now'}")

    return summary


def build_preparedness_bar_data(qs):
    labels = []
    values = []
    colors = []
    keys = []
    for value, label in AssessmentResponse.PREPAREDNESS_LEVEL_CHOICES:
        labels.append(label)
        values.append(qs.filter(preparedness_level=value).count())
        colors.append(LEVEL_COLORS[value])
        keys.append(value)

    return {
        'labels': labels,
        'values': values,
        'colors': colors,
        'keys': keys,
    }


def build_location_pie_data(qs):
    labels = []
    values = []
    keys = []
    for value, label in AssessmentResponse.LOCATION_CHOICES:
        count = qs.filter(location_type=value).count()
        if count > 0:
            labels.append(label)
            values.append(count)
            keys.append(value)

    return {
        'labels': labels,
        'values': values,
        'keys': keys,
    }


def build_emergency_kit_donut_data(qs):
    with_kit = qs.filter(has_emergency_kit=True).count()
    without_kit = qs.filter(has_emergency_kit=False).count()
    return {
        'labels': ['Have Emergency Kit', 'No Emergency Kit'],
        'values': [with_kit, without_kit],
        'keys': ['with_kit', 'without_kit'],
        'colors': ['#2f9e44', '#dc3545'],
    }


def build_trend_line_data(qs):
    trend_rows = list(
        qs.annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(avg_score=Avg('preparedness_score'), assessments=Count('id'))
        .order_by('day')
    )

    return {
        'dates': [row['day'].strftime('%Y-%m-%d') for row in trend_rows],
        'average_scores': [round(row['avg_score'] or 0, 2) for row in trend_rows],
        'assessments': [row['assessments'] for row in trend_rows],
    }


def build_category_comparison_data(qs):
    series = []
    categories = [label for _, label in READINESS_METRICS[:-1]]

    for level_value, level_label in AssessmentResponse.PREPAREDNESS_LEVEL_CHOICES:
        subset = qs.filter(preparedness_level=level_value)
        total = subset.count()
        percentages = []
        for field_name, _ in READINESS_METRICS[:-1]:
            if total == 0:
                percentages.append(0)
            else:
                percentages.append(round((subset.filter(**{field_name: True}).count() / total) * 100, 1))
        series.append(
            {
                'level': level_value,
                'label': level_label,
                'values': percentages,
                'color': LEVEL_COLORS[level_value],
            }
        )

    return {
        'categories': categories,
        'series': series,
    }


def build_preparedness_radar_data(qs):
    total = qs.count()
    categories = []
    values = []
    keys = []

    for field_name, label in READINESS_METRICS:
        categories.append(label)
        keys.append(field_name)
        if field_name == 'self_rated_preparedness':
            average_self_rating = qs.aggregate(avg_value=Avg(field_name))['avg_value'] or 0
            values.append(round((average_self_rating / 5) * 100, 1))
        else:
            values.append(round((qs.filter(**{field_name: True}).count() / total) * 100, 1) if total else 0)

    return {
        'categories': categories,
        'values': values,
        'keys': keys,
    }


def build_score_heatmap_data(qs):
    location_rows = list(AssessmentResponse.LOCATION_CHOICES)
    size_columns = list(FAMILY_SIZE_OPTIONS)
    matrix = []

    for location_value, _ in location_rows:
        row = []
        location_subset = qs.filter(location_type=location_value)
        for family_value, _ in size_columns:
            band_subset = apply_family_size_filter(location_subset, family_value)
            avg_score = band_subset.aggregate(avg=Avg('preparedness_score'))['avg']
            row.append(round(avg_score, 1) if avg_score is not None else None)
        matrix.append(row)

    return {
        'rows': [label for _, label in location_rows],
        'row_keys': [value for value, _ in location_rows],
        'columns': [label for _, label in size_columns],
        'column_keys': [value for value, _ in size_columns],
        'values': matrix,
    }


def build_drilldown_payload(chart, params):
    """Build drill-down panel payload based on clicked chart data point."""
    chart = chart or ''
    base_qs = get_filtered_queryset(params)
    drilldown_qs = base_qs
    title = 'Detailed Assessment Records'
    description = 'Live assessment records matching your selection.'

    if chart == 'preparedness_bar':
        level = params.get('value')
        drilldown_qs = get_filtered_queryset(params, exclude_keys={'preparedness_level'}, overrides={'preparedness_level': level})
        title = f"Preparedness Drill-Down: {dict(AssessmentResponse.PREPAREDNESS_LEVEL_CHOICES).get(level, level)}"
        description = 'Records grouped by preparedness level.'

    elif chart == 'location_pie':
        location = params.get('value')
        drilldown_qs = get_filtered_queryset(params, exclude_keys={'location_type'}, overrides={'location_type': location})
        title = f"Location Drill-Down: {dict(AssessmentResponse.LOCATION_CHOICES).get(location, location)}"
        description = 'Assessments for the selected location type.'

    elif chart == 'emergency_kit_donut':
        value = params.get('value')
        has_kit = value == 'with_kit'
        drilldown_qs = get_filtered_queryset(params).filter(has_emergency_kit=has_kit)
        title = 'Emergency Kit Drill-Down'
        description = 'Assessments segmented by emergency-kit availability.'

    elif chart == 'trend_line':
        day_value = params.get('value')
        drilldown_qs = get_filtered_queryset(params).filter(created_at__date=day_value)
        title = f'Trend Drill-Down: {day_value}'
        description = 'Assessments captured on the selected date.'

    elif chart == 'category_comparison':
        level = params.get('level')
        category = params.get('category')
        field_name = next((field for field, label in READINESS_METRICS if label == category), None)
        drilldown_qs = get_filtered_queryset(params, exclude_keys={'preparedness_level'}, overrides={'preparedness_level': level})
        if field_name and field_name != 'self_rated_preparedness':
            drilldown_qs = drilldown_qs.filter(**{field_name: True})
        title = f'Category Comparison: {category} / {dict(AssessmentResponse.PREPAREDNESS_LEVEL_CHOICES).get(level, level)}'
        description = 'Preparedness category performance inside the selected segment.'

    elif chart == 'preparedness_radar':
        metric = params.get('metric')
        field_name = params.get('field')
        drilldown_qs = get_filtered_queryset(params)
        if field_name and field_name != 'self_rated_preparedness':
            drilldown_qs = drilldown_qs.filter(**{field_name: False})
            description = 'Showing records missing the selected readiness capability.'
        else:
            description = 'Showing records behind the selected radar metric.'
        title = f'Radar Drill-Down: {metric}'

    elif chart == 'score_heatmap':
        location_type = params.get('location_type_key')
        family_size = params.get('family_size_key')
        drilldown_qs = get_filtered_queryset(
            params,
            exclude_keys={'location_type', 'family_size'},
            overrides={'location_type': location_type, 'family_size': family_size},
        )
        title = 'Heatmap Drill-Down'
        description = 'Assessments inside the selected location and family-size cell.'

    records = [serialize_record(record) for record in drilldown_qs[:50]]
    average_score = round(drilldown_qs.aggregate(avg=Avg('preparedness_score'))['avg'] or 0, 1)

    return {
        'title': title,
        'description': description,
        'count': drilldown_qs.count(),
        'average_score': average_score,
        'records': records,
    }


def serialize_record(record):
    return {
        'id': record.id,
        'created_at': record.created_at.strftime('%Y-%m-%d %H:%M'),
        'preparedness_score': round(record.preparedness_score, 1),
        'preparedness_level': record.get_preparedness_level_display(),
        'location_type': record.get_location_type_display(),
        'household_size': record.household_size,
        'housing_type': record.get_housing_type_display(),
        'has_emergency_kit': 'Yes' if record.has_emergency_kit else 'No',
        'has_water_storage': 'Yes' if record.has_water_storage else 'No',
        'has_evacuation_plan': 'Yes' if record.has_evacuation_plan else 'No',
    }


def risk_analysis(request):
    """Dynamic, assessment-driven disaster preparedness analysis page."""
    response_id = request.GET.get('response_id')
    selected_response = None

    if response_id:
        selected_response = get_object_or_404(AssessmentResponse, id=response_id)
    else:
        selected_response = AssessmentResponse.objects.first()

    if not selected_response:
        return render(request, 'assessment/risk_analysis.html', {'no_data': True})

    analysis = analyze_assessment(selected_response)
    context = {
        'response': selected_response,
        'disaster_analysis': analysis['disasters'],
        'overall_score': analysis['overall_score'],
        'overall_level': selected_response.get_preparedness_level_display(),
        'overall_class': analysis['overall_class'],
        'highest_risk': analysis['highest_risk'],
        'strongest_disaster': analysis['strongest_disaster'],
        'priority_actions': analysis['priority_actions'],
        'radar_chart': analysis['radar'],
        'assessment_count': AssessmentResponse.objects.count(),
    }
    return render(request, 'assessment/risk_analysis.html', context)


def recommendations(request):
    """Recommendations page."""
    latest_response = AssessmentResponse.objects.first()

    general_tips = [
        {
            'category': 'Emergency Kit',
            'icon': '🎒',
            'items': ['Water (3-day supply)', 'Non-perishable food', 'Flashlight', 'First-aid kit'],
        },
        {
            'category': 'Family Plan',
            'icon': '👨‍👩‍👧‍👦',
            'items': ['Meeting points', 'Communication plan', 'Evacuation routes'],
        },
    ]

    personalized_tips = []
    if latest_response and not latest_response.has_emergency_kit:
        personalized_tips.append('⚠️ Priority: Prepare emergency kit')

    return render(
        request,
        'assessment/recommendations.html',
        {'general_tips': general_tips, 'personalized_tips': personalized_tips},
    )

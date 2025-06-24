from django.contrib.auth.decorators import login_required
from main.models import Place
from django.shortcuts import render
import json
from django.http import JsonResponse


@login_required(login_url='/login/')
def home_view(request):
    places = Place.objects.all()
    places_json = [
        {
            'id': p.id,
            'name': p.name,
            'latitude': p.latitude,
            'longitude': p.longitude,
            'description': p.description,
            'sport_type': p.sport_type,
            'image_url': p.image_url,
            'open_time': p.open_time.strftime('%H:%M') if p.open_time else '',
            'close_time': p.close_time.strftime('%H:%M') if p.close_time else '',
            'open_days': p.open_days,
        } for p in places
    ]
    return render(request, 'home/home.html', {'places': json.dumps(places_json)})



@login_required(login_url='/login/')
def search_places(request):
    q = request.GET.get('q', '')
    results = []
    if q:
        places = Place.objects.filter(name__icontains=q)[:10]  # limit to 10 results
        for place in places:
            results.append({
                'id': place.id,
                'name': place.name,
                'latitude': place.latitude,
                'longitude': place.longitude,
                'sport_type': place.sport_type,
                'image_url': place.image_url,
                'open_time': place.open_time.strftime('%H:%M') if place.open_time else '',
                'close_time': place.close_time.strftime('%H:%M') if place.close_time else '',
                'open_days': place.open_days,
                'description': place.description,
            })
    return JsonResponse(results, safe=False)
from collections import defaultdict
from datetime import datetime
import json

from django.http import JsonResponse
from django.shortcuts import render

from smartimpulse.apps.graphs.models import GraphsCategory, GraphsData


def graphs(request):
    return render(request, "index.html", {})


def to_ms(dt):
    return int(dt.strftime("%s")) * 1000


def power(request):

    categories = GraphsCategory.objects.all()

    result = {"categories": [category.name for category in categories], "data": {}}

    for data in GraphsData.objects.order_by("dt"):
        date_ms = to_ms(data.dt)
        json_data = json.loads(data.json_data)
        result["data"][date_ms] = {"sum": int(data.power)}
        for category in categories:
            result["data"][date_ms][category.name] = json_data.get(str(category.id), 0)

    return JsonResponse(result)


def energy(request):

    categories = GraphsCategory.objects.all()

    result = {
        "categories": [category.name for category in categories],
        "data": defaultdict(lambda: defaultdict(int)),
    }

    for data in GraphsData.objects.order_by("dt"):
        date = data.dt
        date_ms = to_ms(datetime(year=date.year, month=date.month, day=date.day))
        json_data = json.loads(data.json_data)
        result["data"][date_ms]["sum"] += int(data.power) / 6
        for category in categories:
            result["data"][date_ms][category.name] += (
                json_data.get(str(category.id), 0) / 6
            )

    return JsonResponse(result)

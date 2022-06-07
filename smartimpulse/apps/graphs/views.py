from collections import defaultdict
from datetime import datetime
import json

from django.http import JsonResponse
from django.shortcuts import render

from smartimpulse.apps.graphs.models import (
    GraphsCategory,
    GraphsData,
    GraphsInstallation,
)


def graphs(request):
    return render(request, "index.html", {})


def installations(request):
    installations = GraphsInstallation.objects.all()
    result = {"data": [installation.name for installation in installations]}
    return JsonResponse(result)


def get_installation(request):
    return request.GET["installation"]


def power(request):

    installation = get_installation(request)

    categories = GraphsCategory.objects.all()

    result = {"categories": [category.name for category in categories], "data": {}}

    for data in GraphsData.objects.order_by("dt").filter(
        installation__name=installation
    ):
        date_ms = data.dt.timestamp()
        json_data = json.loads(data.json_data)
        result["data"][date_ms] = {"Total": int(data.power)}
        for category in categories:
            result["data"][date_ms][category.name] = json_data.get(str(category.id), 0)

    return JsonResponse(result)


def energy(request):

    installation = get_installation(request)

    categories = GraphsCategory.objects.all()

    result = {
        "categories": [category.name for category in categories],
        "data": defaultdict(lambda: defaultdict(int)),
    }

    for data in GraphsData.objects.order_by("dt").filter(
        installation__name=installation
    ):
        date = data.dt
        date_ms = datetime(year=date.year, month=date.month, day=date.day).timestamp()
        json_data = json.loads(data.json_data)
        result["data"][date_ms]["Total"] += int(data.power) / 6
        for category in categories:
            result["data"][date_ms][category.name] += (
                json_data.get(str(category.id), 0) / 6
            )

    return JsonResponse(result)

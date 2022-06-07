from datetime import datetime
import json

from bs4 import BeautifulSoup
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from smartimpulse.apps.graphs.models import (
    GraphsCategory,
    GraphsData,
    GraphsInstallation,
)


class GraphsTestCase(TestCase):
    def setUp(self):
        self.category_1 = GraphsCategory.objects.create(name="category_1")
        self.category_2 = GraphsCategory.objects.create(name="category_2")
        self.installation_1 = GraphsInstallation.objects.create(name="installation_1")
        self.installation_2 = GraphsInstallation.objects.create(name="installation_2")
        self.now = timezone.now()
        self.graphs_data = GraphsData.objects.create(
            dt=self.now,
            power=6,
            json_data=json.dumps({str(self.category_1.id): 6}),
            installation=self.installation_1,
        )

    def test_graphs(self):
        response = self.client.get(reverse("graphs"))
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, features="html.parser")
        [title] = soup.find_all("title")
        assert title.get_text() == "Test métier Smart Impulse"

    def test_installations(self):
        response = self.client.get(reverse("installations"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {"data": ["installation_1", "installation_2"]}
        )

    def test_power(self):
        now_ms = str(self.now.timestamp())
        response = self.client.get(
            f"{reverse('power')}?installation={self.installation_1.name}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "categories": ["category_1", "category_2"],
                "data": {now_ms: {"Total": 6, "category_1": 6, "category_2": 0}},
            },
        )

    def test_energy(self):
        today_ms = str(
            datetime(
                year=self.now.year, month=self.now.month, day=self.now.day
            ).timestamp()
        )
        response = self.client.get(
            f"{reverse('energy')}?installation={self.installation_1.name}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "categories": ["category_1", "category_2"],
                "data": {
                    today_ms: {
                        "Total": 1,
                        "category_1": 1.0,
                        "category_2": 0.0,
                    }
                },
            },
        )

from datetime import datetime
import json

from bs4 import BeautifulSoup
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from smartimpulse.apps.graphs.models import (
    GraphsCategory,
    GraphsData,
    GraphsInstallation,
)
from smartimpulse.apps.graphs.views import to_ms


class GraphsTestCase(TestCase):
    def setUp(self):
        self.category_1 = GraphsCategory(name="category_1")
        self.category_1.save()
        self.category_2 = GraphsCategory(name="category_2")
        self.category_2.save()
        self.installation_1 = GraphsInstallation(name="installation_1")
        self.installation_1.save()
        self.installation_2 = GraphsInstallation(name="installation_2")
        self.installation_2.save()
        self.now = timezone.now()
        self.graphs_data = GraphsData(
            dt=self.now,
            power=6,
            json_data=json.dumps({str(self.category_1.id): 6}),
            installation=self.installation_1,
        )
        self.graphs_data.save()

    def test_graphs(self):
        client = Client()
        response = client.get(reverse("graphs"))
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, features="html.parser")
        [title] = soup.find_all("title")
        assert title.get_text() == "Test métier Smart Impulse"

    def test_installations(self):
        client = Client()
        response = client.get(reverse("installations"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {"data": ["installation_1", "installation_2"]}
        )

    def test_power(self):
        now_ms = str(to_ms(self.now))
        client = Client()
        response = client.get(
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
            to_ms(datetime(year=self.now.year, month=self.now.month, day=self.now.day))
        )
        client = Client()
        response = client.get(
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

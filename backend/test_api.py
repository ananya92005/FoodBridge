from datetime import timedelta
from unittest.mock import AsyncMock, patch

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from assignments.models import Assignment, AssignmentStatus
from authentication.models import UserRole
from config.asgi import application
from food.models import FoodListing, FoodStatus
from ngo.models import NGO
from notifications.models import Notification


class FoodBridgeApiTests(APITestCase):
    def make_user(self, email, password, first_name, last_name, role):
        user = get_user_model()(
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
        )
        user.set_password(password)
        user.save()
        return user

    def setUp(self):
        self.donor = self.make_user(
            email="donor@example.test",
            password="DonorPass123!",
            first_name="Food",
            last_name="Donor",
            role=UserRole.DONOR,
        )
        self.ngo_user = self.make_user(
            email="ngo@example.test",
            password="NgoPass123!",
            first_name="Community",
            last_name="NGO",
            role=UserRole.NGO,
        )
        self.ngo = NGO.objects.create(
            user=self.ngo_user,
            name="Community Pantry",
            city="Test City",
            district="Test District",
            capacity=100,
            latitude=0.0,
            longitude=0.01,
        )
        self.listing = self.make_listing()

    def make_listing(self, food_type="Fresh produce"):
        return FoodListing.objects.create(
            donor=self.donor,
            food_type=food_type,
            quantity=10,
            description="Good condition",
            expiry_time=timezone.now() + timedelta(hours=12),
            latitude=0.0,
            longitude=0.0,
        )

    def test_api_indexes_and_admin_route(self):
        for url in ("/", "/api/", "/api/auth/"):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get("/admin/").status_code, status.HTTP_302_FOUND)

    def test_registration_login_refresh_and_current_user(self):
        credentials = {
            "email": "new-donor@example.test",
            "password": "FoodPass123!",
            "first_name": "New",
            "last_name": "Donor",
            "role": UserRole.DONOR,
        }
        registered = self.client.post("/api/auth/register/", credentials, format="json")
        self.assertEqual(registered.status_code, status.HTTP_201_CREATED, registered.data)
        self.assertIn("access", registered.data)
        self.assertIn("refresh", registered.data)

        admin_registration = self.client.post(
            "/api/auth/register/",
            {**credentials, "email": "public-admin@example.test", "role": UserRole.ADMIN},
            format="json",
        )
        self.assertEqual(admin_registration.status_code, status.HTTP_400_BAD_REQUEST)

        logged_in = self.client.post(
            "/api/auth/login/",
            {"email": credentials["email"], "password": credentials["password"]},
            format="json",
        )
        self.assertEqual(logged_in.status_code, status.HTTP_200_OK, logged_in.data)
        refreshed = self.client.post(
            "/api/auth/refresh/", {"refresh": logged_in.data["refresh"]}, format="json"
        )
        self.assertEqual(refreshed.status_code, status.HTTP_200_OK, refreshed.data)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {logged_in.data['access']}")
        current_user = self.client.get("/api/auth/me/")
        self.assertEqual(current_user.status_code, status.HTTP_200_OK)
        self.assertEqual(current_user.data["email"], credentials["email"])

    def test_users_and_food_listing_endpoints(self):
        self.client.force_authenticate(self.donor)
        users = self.client.get("/api/users/?role=NGO")
        self.assertEqual(users.status_code, status.HTTP_200_OK)
        self.assertEqual(users.data[0]["role"], UserRole.NGO)

        listings = self.client.get("/api/food/listings/")
        self.assertEqual(listings.status_code, status.HTTP_200_OK)
        self.assertEqual(len(listings.data), 1)

        created = self.client.post(
            "/api/food/listings/",
            {
                "food_type": "Bread",
                "quantity": 5,
                "description": "Fresh bread",
                "expiry_time": (timezone.now() + timedelta(days=1)).isoformat(),
                "latitude": 0.0,
                "longitude": 0.0,
            },
            format="json",
        )
        self.assertEqual(created.status_code, status.HTTP_201_CREATED, created.data)
        listing_id = created.data["id"]
        self.assertEqual(created.data["status"], FoodStatus.MATCHED)

        detail_url = f"/api/food/listings/{listing_id}/"
        detail = self.client.get(detail_url)
        self.assertEqual(detail.status_code, status.HTTP_200_OK, {"id": listing_id, "response": detail.data})
        replaced = self.client.put(
            detail_url,
            {
                "food_type": "Bread",
                "quantity": 6,
                "description": "Replaced details",
                "expiry_time": (timezone.now() + timedelta(days=1)).isoformat(),
                "latitude": 0.0,
                "longitude": 0.0,
            },
            format="json",
        )
        self.assertEqual(replaced.status_code, status.HTTP_200_OK, replaced.data)
        updated = self.client.patch(detail_url, {"description": "Updated details"}, format="json")
        self.assertEqual(updated.status_code, status.HTTP_200_OK, updated.data)

        self.client.force_authenticate(self.ngo_user)
        self.assertEqual(
            self.client.post("/api/food/listings/", {}, format="json").status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(self.client.get(f"/api/food/listings/{self.listing.id}/").status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.client.patch(f"/api/food/listings/{self.listing.id}/", {"quantity": 1}, format="json").status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(self.client.delete(f"/api/food/listings/{self.listing.id}/").status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(self.donor)
        self.assertEqual(self.client.delete(detail_url).status_code, status.HTTP_204_NO_CONTENT)

    def test_ngo_profile_and_nearby_food_endpoints(self):
        self.client.force_authenticate(self.ngo_user)
        self.assertEqual(self.client.get("/api/ngo/profile/").status_code, status.HTTP_200_OK)
        profile = {
            "name": "Community Pantry",
            "city": "Test City",
            "district": "Test District",
            "capacity": 100,
            "latitude": 0.0,
            "longitude": 0.01,
            "is_active": True,
        }
        self.assertEqual(self.client.put("/api/ngo/profile/", profile, format="json").status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.patch("/api/ngo/profile/", {"capacity": 120}, format="json").status_code, status.HTTP_200_OK)
        nearby = self.client.get("/api/ngo/nearby-food/?distance=25")
        self.assertEqual(nearby.status_code, status.HTTP_200_OK)
        self.assertEqual(len(nearby.data), 1)

        self.client.force_authenticate(self.donor)
        self.assertEqual(self.client.get("/api/ngo/profile/").status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.get("/api/ngo/nearby-food/").status_code, status.HTTP_403_FORBIDDEN)

    def test_matching_and_route_estimate_endpoints(self):
        self.client.force_authenticate(self.donor)
        matches = self.client.post(
            "/api/matching/preview/", {"listing_id": self.listing.id}, format="json"
        )
        self.assertEqual(matches.status_code, status.HTTP_200_OK, matches.data)
        self.assertEqual(matches.data[0]["ngo_id"], self.ngo.id)

        estimate = self.client.post(
            "/api/routing/estimate/",
            {
                "origin": {"latitude": 0.0, "longitude": 0.0},
                "destination": {"latitude": 0.0, "longitude": 1.0},
            },
            format="json",
        )
        self.assertEqual(estimate.status_code, status.HTTP_200_OK, estimate.data)
        self.assertGreater(estimate.data["distance_km"], 100)
        self.assertGreater(estimate.data["estimated_minutes"], 0)

    def test_assignment_and_notification_endpoints(self):
        assignment = Assignment.objects.create(food=self.listing, ngo=self.ngo)
        self.client.force_authenticate(self.donor)
        self.assertEqual(self.client.get("/api/assignments/").status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.client.post(f"/api/assignments/{assignment.id}/accept/").status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.client.force_authenticate(self.ngo_user)
        self.assertEqual(self.client.get("/api/assignments/").status_code, status.HTTP_200_OK)
        accepted = self.client.post(f"/api/assignments/{assignment.id}/accept/")
        self.assertEqual(accepted.status_code, status.HTTP_200_OK, accepted.data)
        self.assertEqual(accepted.data["status"], AssignmentStatus.ACCEPTED)

        rejected_listing = self.make_listing("Vegetables")
        rejected_assignment = Assignment.objects.create(food=rejected_listing, ngo=self.ngo)
        rejected = self.client.post(f"/api/assignments/{rejected_assignment.id}/reject/")
        self.assertEqual(rejected.status_code, status.HTTP_200_OK, rejected.data)
        self.assertEqual(rejected.data["status"], AssignmentStatus.REJECTED)

        completed_listing = self.make_listing("Fruit")
        completed_assignment = Assignment.objects.create(food=completed_listing, ngo=self.ngo)
        completed = self.client.post(f"/api/assignments/{completed_assignment.id}/complete/")
        self.assertEqual(completed.status_code, status.HTTP_200_OK, completed.data)
        self.assertEqual(completed.data["status"], AssignmentStatus.COMPLETED)

        invalid_action = self.client.post(f"/api/assignments/{assignment.id}/unknown/")
        self.assertEqual(invalid_action.status_code, status.HTTP_400_BAD_REQUEST)

        self.client.force_authenticate(self.donor)
        notifications = self.client.get("/api/notifications/")
        self.assertEqual(notifications.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(notifications.data), 1)
        notification = Notification.objects.filter(user=self.donor).first()
        marked_read = self.client.post(f"/api/notifications/{notification.id}/read/")
        self.assertEqual(marked_read.status_code, status.HTTP_200_OK)
        self.assertTrue(marked_read.data["is_read"])

    def test_protected_endpoints_require_authentication(self):
        protected_gets = (
            "/api/auth/me/",
            "/api/users/",
            "/api/food/listings/",
            "/api/ngo/profile/",
            "/api/ngo/nearby-food/",
            "/api/notifications/",
            "/api/assignments/",
        )
        for url in protected_gets:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, status.HTTP_401_UNAUTHORIZED)

        self.assertEqual(
            self.client.post("/api/matching/preview/", {"listing_id": self.listing.id}, format="json").status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertEqual(
            self.client.post(
                "/api/routing/estimate/",
                {
                    "origin": {"latitude": 0, "longitude": 0},
                    "destination": {"latitude": 1, "longitude": 1},
                },
                format="json",
            ).status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_notification_websocket_authentication_and_delivery(self):
        async def check_websocket():
            anonymous = WebsocketCommunicator(application, "/ws/notifications/")
            connected, _ = await anonymous.connect()
            self.assertFalse(connected)

            with patch("notifications.auth.get_user_from_token", new=AsyncMock(return_value=self.ngo_user)):
                communicator = WebsocketCommunicator(
                    application,
                    "/ws/notifications/?token=test-token",
                )
                connected, _ = await communicator.connect()
                self.assertTrue(connected)

                payload = {"message": "notification test"}
                await get_channel_layer().group_send(
                    f"user_{self.ngo_user.id}",
                    {"type": "notify.message", "payload": payload},
                )
                received = await communicator.receive_json_from(timeout=1)
                self.assertEqual(received, payload)
                await communicator.disconnect()

        async_to_sync(check_websocket)()

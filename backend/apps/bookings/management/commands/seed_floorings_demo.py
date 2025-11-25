from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from apps.floors.models import FloorPlan, Room
from apps.bookings.models import Booking

User = get_user_model()


class Command(BaseCommand):
    help = "Seed demo data for the Floorings frontend (users, floors, rooms, bookings)."

    def handle(self, *args, **options):
        admin_username = "admin_demo"
        admin_password = "Admin@1234"
        employee_username = "employee_demo"
        employee_password = "Employee@1234"

        admin_user, created_admin = User.objects.get_or_create(
            username=admin_username,
            defaults={
                "is_staff": True,
                "is_superuser": True,
                "email": "admin_demo@example.com",
            },
        )
        if created_admin:
            admin_user.set_password(admin_password)
            admin_user.save()

        employee_user, created_employee = User.objects.get_or_create(
            username=employee_username,
            defaults={
                "is_staff": False,
                "is_superuser": False,
                "email": "employee_demo@example.com",
            },
        )
        if created_employee:
            employee_user.set_password(employee_password)
            employee_user.save()

        floor1, _ = FloorPlan.objects.get_or_create(
            name="MoveInSync HQ - Floor 1",
            defaults={"floor_number": 1},
        )
        floor2, _ = FloorPlan.objects.get_or_create(
            name="MoveInSync HQ - Floor 2",
            defaults={"floor_number": 2},
        )

        room1, _ = Room.objects.get_or_create(
            floor_plan=floor1,
            room_number="A101",
            defaults={
                "name": "Aurora Conference",
                "capacity": 10,
                "room_type": "CONFERENCE",
                "is_active": True,
            },
        )
        room2, _ = Room.objects.get_or_create(
            floor_plan=floor1,
            room_number="A102",
            defaults={
                "name": "Orion Huddle",
                "capacity": 4,
                "room_type": "HUDDLE",
                "is_active": True,
            },
        )
        room3, _ = Room.objects.get_or_create(
            floor_plan=floor2,
            room_number="B201",
            defaults={
                "name": "Nebula Board Room",
                "capacity": 16,
                "room_type": "CONFERENCE",
                "is_active": True,
            },
        )

        now = timezone.now()
        Booking.objects.get_or_create(
            room=room1,
            user=employee_user,
            start_time=now + timedelta(hours=1),
            end_time=now + timedelta(hours=2),
            defaults={
                "participants_count": 6,
                "purpose": "Project sync-up",
            },
        )
        Booking.objects.get_or_create(
            room=room2,
            user=employee_user,
            start_time=now + timedelta(days=1, hours=2),
            end_time=now + timedelta(days=1, hours=3),
            defaults={
                "participants_count": 3,
                "purpose": "Design review",
            },
        )

        self.stdout.write(self.style.SUCCESS("Demo data seeding complete."))
        self.stdout.write(self.style.SUCCESS("Admin login:    admin_demo / Admin@1234"))
        self.stdout.write(self.style.SUCCESS("Employee login: employee_demo / Employee@1234"))

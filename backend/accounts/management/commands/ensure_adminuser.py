from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Creates an admin user if it does not exist"

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True, help="Admin email")
        parser.add_argument("--password", required=True, help="Admin password")

    def handle(self, *args, **options):
        user_model = get_user_model()
        email = options["email"].strip().lower()
        if user_model.objects.filter(email__iexact=email).exists():
            self.stdout.write(f"Superuser {email} already exists")
            return

        user_model.objects.create_superuser(
            email=email, full_name=email, password=options["password"]
        )
        self.stdout.write(f"Superuser {email} created")

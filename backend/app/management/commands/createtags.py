from django.core.management.base import BaseCommand
from django.db import transaction
from app.models import Tag


class Command(BaseCommand):
    @transaction.atomic()
    def handle(self, *args, **options):
        if Tag.objects.filter().exists():
            self.stdout.write(self.style.ERROR("Tags exist. Stopping"))
            return
        for name in ["Car", "Bike", "Bad Parking", "Mosquito", "Snail"]:
            Tag.create(name=name)
        self.stdout.write(self.style.SUCCESS("Loaded tags"))

from collections import defaultdict
import os

from django.apps import apps
from django.conf import settings
from django.contrib.gis import geos
from django.contrib.gis.gdal import DataSource
from django.core.management.base import BaseCommand
from django.db import transaction
from app.models import CivicArea, CivicPoint


def absolute_path(path: str) -> str:
    return os.path.join(settings.BASE_DIR, path)

# From https://www.caktusgroup.com/blog/2019/01/09/django-bulk-inserts/
class BulkCreateManager(object):
    """
    This helper class keeps track of ORM objects to be created for multiple
    model classes, and automatically creates those objects with `bulk_create`
    when the number of objects accumulated for a given model class exceeds
    `chunk_size`.
    Upon completion of the loop that's `add()`ing objects, the developer must
    call `done()` to ensure the final set of objects is created for all models.
    """

    def __init__(self, chunk_size=100):
        self._create_queues = defaultdict(list)
        self.chunk_size = chunk_size

    def _commit(self, model_class):
        model_key = model_class._meta.label
        model_class.objects.bulk_create(self._create_queues[model_key])
        self._create_queues[model_key] = []

    def add(self, obj):
        """
        Add an object to the queue to be created, and call bulk_create if we
        have enough objs.
        """
        model_class = type(obj)
        model_key = model_class._meta.label
        self._create_queues[model_key].append(obj)
        if len(self._create_queues[model_key]) >= self.chunk_size:
            self._commit(model_class)

    def done(self):
        """
        Always call this upon completion to make sure the final partial chunk
        is saved.
        """
        for model_name, objs in self._create_queues.items():
            if len(objs) > 0:
                self._commit(apps.get_model(model_name))


bulk_create_manager = BulkCreateManager()


class Command(BaseCommand):
    @transaction.atomic()
    def handle(self, *args, **options):
        CivicArea.objects.filter().delete()
        CivicPoint.objects.filter().delete()

        states_source = DataSource(
            absolute_path(
                "geo-data/India_Boundary_Updated/Indian_State_Boundary/India_State_Boundary_Updated.shp"
            )
        )
        for state in states_source[0]:
            state_name = str(state["stname"])
            polygon = state.geom.geos
            # TypeError: Cannot set State2 SpatialProxy (MULTIPOLYGON) with value of type: <class 'django.contrib.gis.geos.polygon.Polygon'>
            if not isinstance(polygon, geos.MultiPolygon):
                polygon = geos.MultiPolygon(polygon)
            bulk_create_manager.add(CivicArea(name=state_name, area=polygon))
            print(f"State: {state_name}")
        bulk_create_manager.done()

        # districts = [
        #     'Tamil_Nadu_Boundary/Tamil_Nadu_Boundary_Updated.shp',
        #     'Indian_District_Boundary/stname_WEST BENGAL.gpkg',
        #     'Indian_District_Boundary/stname_CHANDIGARH.gpkg',
        #     'Indian_District_Boundary/stname_HARYANA.gpkg',
        #     'Indian_District_Boundary/stname_ANDHRA PRADESH.gpkg',
        #     'Indian_District_Boundary/stname_JAMMU & KASHMIR.gpkg',
        #     'Indian_District_Boundary/stname_LADAKH.gpkg',
        #     'Indian_District_Boundary/stname_TELANGANA.gpkg',
        #     'Indian_District_Boundary/stname_JHARKHAND.gpkg',
        #     'Indian_District_Boundary/stname_PUNJAB.gpkg',
        #     'Indian_District_Boundary/stname_MEGHALAYA.gpkg',
        #     'Indian_District_Boundary/stname_ODISHA.gpkg',
        #     'Indian_District_Boundary/stname_TRIPURA.gpkg',
        #     'Indian_District_Boundary/stname_GUJARAT.gpkg',
        #     'Indian_District_Boundary/stname_ANDAMAN & NICOBAR.gpkg',
        #     'Indian_District_Boundary/stname_DELHI.gpkg',
        #     'Indian_District_Boundary/stname_DADRA & NAGAR HAVE.gpkg',
        #     'Indian_District_Boundary/stname_DAMAN & DIU.gpkg',
        #     'Indian_District_Boundary/stname_LAKSHADWEEP.gpkg',
        #     'Indian_District_Boundary/stname_HIMACHAL PRADESH.gpkg',
        #     'Indian_District_Boundary/stname_UTTARAKHAND.gpkg',
        #     'Indian_District_Boundary/stname_MIZORAM.gpkg',
        #     'Indian_District_Boundary/stname_RAJASTHAN.gpkg',
        #     'Indian_District_Boundary/stname_PUDUCHERRY.gpkg',
        #     'Indian_District_Boundary/stname_MADHYA PRADESH.gpkg',
        #     'Indian_District_Boundary/stname_BIHAR.gpkg',
        #     'Indian_District_Boundary/stname_MAHARASHTRA.gpkg',
        #     'Indian_District_Boundary/stname_KARNATAKA.gpkg',
        #     'Indian_District_Boundary/stname_MANIPUR.gpkg',
        #     'Indian_District_Boundary/stname_NAGALAND.gpkg',
        #     'Indian_District_Boundary/stname_CHHATTISGARH.gpkg',
        #     'Indian_District_Boundary/stname_ARUNACHAL PRADESH.gpkg',
        #     'Indian_District_Boundary/stname_UTTAR PRADESH.gpkg',
        #     'Indian_District_Boundary/stname_GOA.gpkg',
        #     'Indian_District_Boundary/stname_SIKKIM.gpkg',
        #     'Indian_District_Boundary/stname_ASSAM.gpkg',
        #     'Indian_District_Boundary/stname_KERALA.gpkg',]
        #
        # for district_source in districts:
        #     district_source = DataSource('/code/geo-data/India_Boundary_Updated/' + district_source)
        #     for district in district_source[0]:
        #         name = str(district['dtname'])
        #         polygon = district.geom.geos
        #         # TypeError: Cannot set State2 SpatialProxy (MULTIPOLYGON) with value of type: <class 'django.contrib.gis.geos.polygon.Polygon'>
        #         if not isinstance(polygon, geos.MultiPolygon):
        #             polygon = geos.MultiPolygon(polygon)
        #
        #         any_state = State.objects.filter(name=str(district['stname'])).first()
        #         print(any_state)
        #         district = District.objects.create_district(name=name, geometry=polygon, state=any_state)
        #
        # District.objects.update(geometry=Func(F('geometry'), function='ST_FlipCoordinates'),
        #                         centroid=Func(F('centroid'), function='ST_FlipCoordinates'))

        po_source = open(absolute_path("geo-data/IN/IN.txt"), "r", encoding="utf-8")
        scores = {}
        prev_district_name = None
        for line in po_source.readlines():
            (
                _,
                pin_code,
                name,
                state_name,
                _,
                district_name,
                _,
                subdistrict_name,
                _,
                lat,
                lng,
                accuracy,
            ) = line.split("\t")
            if district_name != prev_district_name:
                print(f"Post offices for {district_name}")
                prev_district_name = district_name
            lat = float(lat)
            lng = float(lng)
            accuracy = accuracy.strip()
            if accuracy in scores:
                scores[accuracy] += 1
            else:
                scores[accuracy] = 1
            # todo check if its within service area
            point = geos.Point(lng, lat)
            bulk_create_manager.add(
                CivicPoint(f"{name}, {subdistrict_name}, {district_name}", point)
            )
        bulk_create_manager.done()
        print("accuracy scores", scores)
        self.stdout.write(self.style.SUCCESS("Loaded states and post offices"))

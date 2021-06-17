from django.contrib.gis import geos
from django.contrib.gis.gdal import DataSource
from django.core.management.base import BaseCommand
from django.db import transaction

from app.models import CivicArea, CivicPoint


class Command(BaseCommand):
    @transaction.atomic()
    def handle(self, *args, **options):
        CivicArea.objects.filter().delete()
        CivicPoint.objects.filter().delete()

        states_source = DataSource(
            "/code/backend/geo-data/India_Boundary_Updated/Indian_State_Boundary/India_State_Boundary_Updated.shp"
        )
        for state in states_source[0]:
            state_name = str(state["stname"])
            polygon = state.geom.geos
            # TypeError: Cannot set State2 SpatialProxy (MULTIPOLYGON) with value of type: <class 'django.contrib.gis.geos.polygon.Polygon'>
            if not isinstance(polygon, geos.MultiPolygon):
                polygon = geos.MultiPolygon(polygon)
            CivicArea.create(name=state_name, area=polygon)

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

        po_source = open("/code/backend/geo-data/IN/IN.txt", "r", encoding="utf-8")
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
                print(district_name)
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
            CivicPoint.create(f"{name}, {subdistrict_name}, {district_name}", point)
        print("accuracy scores", scores)
        self.stdout.write(self.style.SUCCESS("Ran this script"))

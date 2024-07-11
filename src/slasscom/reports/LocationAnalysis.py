import hashlib
import os
import pickle
import tempfile
from functools import cache, cached_property, wraps

import googlemaps
from gig import Ent, EntType
from shapely.geometry import Point
from utils import JSONFile, Log

from slasscom.core import Company

log = Log('LocationAnalysis')


def file_cache(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        args_hash = hashlib.md5(pickle.dumps((args, kwargs))).hexdigest()
        cache_file_path = os.path.join(
            tempfile.gettempdir(), f'{func.__name__}.{args_hash}.cache'
        )

        # Check if the cache file exists
        if os.path.exists(cache_file_path):
            with open(cache_file_path, 'rb') as f:
                return pickle.load(f)

        # Call the original function and cache the result
        result = func(*args, **kwargs)
        with open(cache_file_path, 'wb') as f:
            pickle.dump(result, f)
            log.debug(f'Wrote  {cache_file_path}')

        return result

    return wrapper


class CompanyWrapper:
    def __init__(self, company):
        self.company = company

    @cached_property
    @file_cache
    def latlng(self) -> tuple[float, float]:
        google_api_key = os.environ['GMAPS_API_KEY']
        gmaps = googlemaps.Client(key=google_api_key)

        geocode_result = gmaps.geocode(self.company.address)
        if len(geocode_result) == 0:
            raise ValueError(f'No geocode result for {self.company.address}')
        location = geocode_result[0]['geometry']['location']
        return location['lat'], location['lng']

    @file_cache
    def get_region_id(self, region_type, parent_region_id):
        lat, lng = self.latlng
        point = Point(lng, lat)
        ents = Ent.list_from_type(region_type)
        for ent in ents:
            if parent_region_id not in ent.id:
                continue
            geo = ent.geo().buffer(0)
            if geo.contains(point).any():
                return ent.id
        raise ValueError(f'No {region_type} found for {self.company.name}')

    @cached_property
    def province_id(self) -> str:
        return self.get_region_id(EntType.PROVINCE, 'LK')

    @cached_property
    def district_id(self) -> str:
        return self.get_region_id(EntType.DISTRICT, self.province_id)

    @cached_property
    def dsd_id(self) -> str:
        return self.get_region_id(EntType.DSD, self.district_id)

    @cached_property
    def gnd_id(self) -> str:
        return self.get_region_id(EntType.GND, self.dsd_id)

    @cached_property
    def province_name(self) -> str:
        return Ent.from_id(self.province_id).name

    @cached_property
    def district_name(self) -> str:
        return Ent.from_id(self.district_id).name

    @cached_property
    def dsd_name(self) -> str:
        return Ent.from_id(self.dsd_id).name

    @cached_property
    def gnd_name(self) -> str:
        return Ent.from_id(self.gnd_id).name

    @cached_property
    @file_cache
    def location_info(self) -> dict:
        return dict(
            company_name=self.company.name,
            company_address=self.company.address,
            latlng=self.latlng,
            province_id=self.province_id,
            province_name=self.province_name,
            district_id=self.district_id,
            district_name=self.district_name,
            dsd_id=self.dsd_id,
            dsd_name=self.dsd_name,
            gnd_id=self.gnd_id,
            gnd_name=self.gnd_name,
        )


class LocationAnalysis:
    NAME_TO_LOCATION_INFO_PATH = os.path.join(
        'data', 'name_to_location_info.json'
    )

    @cached_property
    def name_to_location_info_nocache(self):
        idx = {}
        company_list = Company.list_all()
        for company in company_list:
            if company.name.lower().startswith('test'):
                log.warning(f'Skipping {company.name}')
                continue
            c = CompanyWrapper(company)
            location_info = c.location_info
            log.debug(location_info)
            idx[company.name] = location_info
            log.debug('...')

        return idx

    @cached_property
    def name_to_location_info(self):
        if os.path.exists(self.NAME_TO_LOCATION_INFO_PATH):
            return JSONFile(self.NAME_TO_LOCATION_INFO_PATH).read()
        name_to_location_info = self.name_to_location_info_nocache
        JSONFile(self.NAME_TO_LOCATION_INFO_PATH).write(name_to_location_info)
        log.debug(f'Wrote {self.NAME_TO_LOCATION_INFO_PATH}.')
        return name_to_location_info

    @cache
    def get_key_to_n(self, func_key: callable, func_filter: callable = None):
        idx = {}
        for location_info in self.name_to_location_info.values():
            if func_filter is not None and not func_filter(location_info):
                continue
            k = func_key(location_info)
            if k not in idx:
                idx[k] = 0
            idx[k] += 1
        idx = dict(sorted(idx.items(), key=lambda x: x[1], reverse=True))
        return idx

    def run(self):
        self.name_to_location_info
        print(self.get_key_to_n(lambda x: x['district_id']))
        print(
            self.get_key_to_n(
                lambda x: x['dsd_id'], lambda x: x['district_id'] == 'LK-11'
            )
        )
        print(
            self.get_key_to_n(
                lambda x: x['gnd_id'],
                lambda x: x['dsd_id'] in ['LK-1127', 'LK-1103'],
            )
        )


if __name__ == "__main__":
    LocationAnalysis().run()

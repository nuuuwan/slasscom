import os
import re
from functools import cached_property

from utils import WWW, JSONFile, Log, Hash

from slasscom.www.DirectoryPage import DirectoryPage

log = Log('CompanyLoader')


class CompanyLoader:
    DIR_DATA = 'data'
    DIR_IMAGES = os.path.join(DIR_DATA, 'images')
    LOCAL_DATA_PATH = os.path.join(DIR_DATA, 'company_d_list.json')

    @classmethod
    def from_dict(cls, d):
        return cls(**d)

    def to_dict(self):
        return self.__dict__

    @classmethod
    def __list_all_from_local(cls):
        company_list = [
            cls.from_dict(d) for d in JSONFile(cls.LOCAL_DATA_PATH).read()
        ]
        log.debug(
            f'Read {len(company_list)} companies from {cls.LOCAL_DATA_PATH}'
        )
        return company_list

    @classmethod
    def __list_all_from_remote(cls):
        page = DirectoryPage()
        page.open()
        d_list = page.get_company_d_list()
        page.quit()
        company_list = [cls.from_dict(d) for d in d_list]

        company_list.sort(key=lambda c: c.name)

        os.makedirs(cls.DIR_DATA, exist_ok=True)
        JSONFile(cls.LOCAL_DATA_PATH).write(
            [c.to_dict() for c in company_list]
        )
        log.info(
            f'Wrote {len(company_list)} companies to {cls.LOCAL_DATA_PATH}'
        )
        return company_list

    @classmethod
    def list_all(cls):
        if os.path.exists(cls.LOCAL_DATA_PATH):
            return cls.__list_all_from_local()
        return cls.__list_all_from_remote()

    @cached_property
    def id(self) -> str:
        name_part = re.sub(r'\W+', '_', self.name.lower())
        h = Hash.md5(self.name)[:8]
        return name_part[:8] + '-' + h
    @cached_property
    def logo_path(self) -> str:
        ext = self.logo_image_url.split('.')[-1]
        logo_path = os.path.join(self.DIR_IMAGES, f'{self.id}.{ext}')
        if not os.path.exists(logo_path):
            WWW.download_binary(self.logo_image_url, logo_path)
            log.info(f'Downloaded {self.logo_image_url} to {logo_path}')
        return logo_path

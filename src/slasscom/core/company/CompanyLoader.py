import os

from utils import JSONFile, Log

from slasscom.www.DirectoryPage import DirectoryPage

log = Log('CompanyLoader')


class CompanyLoader:
    DIR_DATA = 'data'
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

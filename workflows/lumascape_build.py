import os

from lumascape import Lumascape
from slasscom import Company


def main():
    company_list = Company.list_all()
    Lumascape(
        company_list,
        get_name=lambda company: company.name,
        get_group=lambda company: company.core_business_focus,
        get_image_path=lambda company: company.logo_path,
        size=(1600, 900),
    ).write(os.path.join(Company.DIR_DATA, 'lumascape.png'))


if __name__ == "__main__":
    main()

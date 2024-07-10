from dataclasses import dataclass


@dataclass
class CompanyBase:
    name: str
    logo_image_url: str
    core_business_focus: str
    service_sectors: str
    address: str
    telephone: str
    email: str
    website: str

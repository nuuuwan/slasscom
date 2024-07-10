from utils import File, Log

from slasscom.core import Company

log = Log('ReadMe')


class ReadMe:
    PATH = 'README.md'

    def format_telephone(x: str) -> str:
        x = x.strip()
        x = x.replace(' ', '')
        x = x.replace('-', '')
        x = x.replace('(', '')
        x = x.replace(')', '')
        x = x.replace('+94', '00')
        if x.startswith('94'):
            x = '0' + x[2:]
        if len(x) < 10:
            x = '0' * (10 - len(x)) + x

        x = x[-10:]

        assert x[0] == '0'
        assert len(x) == 10

        x_label = f'{x[:3]} {x[3:6]} {x[6:]}'
        return f'[{x_label}](tel:{x})'

    def build_company(self, company: Company) -> list:
        lines = []
        lines.extend([f'## {company.name}', ''])

        lines.extend(
            [f'<img src="{company.logo_image_url}" height="100px"/>', '']
        )

        lines.extend(['|  |  |', '|---|---|'])
        for k, v in company.to_dict().items():
            if k in ['name', 'logo_image_url']:
                continue
            if k in ['core_business_focus', 'service_sectors']:
                v = ', '.join([f'`{x}`' for x in v.split(', ')])
            if k in ['email', 'website']:
                v = f'[{v}]({v})'

            if k == 'telephone':
                v = ReadMe.format_telephone(v)
            lines.append(f'| {k} | {v} |')

        lines.append('')
        return lines

    def build(self):
        company_list = Company.list_all()
        lines = ['# Company List', '']

        for company in company_list:
            lines.extend(self.build_company(company))

        File(ReadMe.PATH).write_lines(lines)
        log.info(f'Wrote {len(company_list)} companies to {ReadMe.PATH}')

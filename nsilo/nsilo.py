import requests
from typing import List
from lxml import etree

# Get apikey
with open('apikey') as f:
    apikey = f.read().strip()

BASEURL = 'https://www.namesilo.com/api/'
BASEOPTS = {
    'version': 1,
    'type': 'xml',
    'key': apikey
}

class NameSiloError(Exception):
    pass

class DomainInfo():
    def __init__(self, resource_record: etree._Element):
        self.id: str = resource_record.findtext('record_id')
        self.type: str = resource_record.findtext('type')
        self.host: str = resource_record.findtext('host')
        self.value: str = resource_record.findtext('value')
        self.ttl: str = resource_record.findtext('ttl')
        self.distance: str = resource_record.findtext('distance')

    def __str__(self):
        obj = {
            'id': self.id,
            'type': self.type,
            'host': self.host,
            'value': self.value,
            'ttl': self.ttl,
            'distance': self.distance
        }
        return str(obj)

class NSilo():
    def __init__(self):
        self.session = requests.session()

    def _send(self, method: str, **kwargs) -> etree._ElementTree:
        opts = BASEOPTS.copy()
        for key, value in kwargs.items():
            opts[key] = value
        res = self.session.get(BASEURL + method, params=opts)
        return etree.fromstring(res.text)

    def list_domains(self):
        res = self._send('listDomains')
        domains = res.xpath('//domain')
        return [x.text for x in domains]
        
    def get_domain_info(self, domain: str):
        res = self._send('getDomainInfo', domain=domain)
        
    def dns_list_records(self, domain: str) -> List[DomainInfo]:
        res = self._send('dnsListRecords', domain=domain)
        records = res.xpath('.//resource_record')
        return [DomainInfo(x) for x in records]
    
    def dns_delete_record(self, domain: str, id: str):
        res = self._send('dnsDeleteRecord', domain=domain, rrid=id)
        code = res.findtext('.//code')
        result = res.findtext('.//detail')
        if code != '300' or result != 'success':
            raise NameSiloError(f'Result code of {code} and result of {result}')

    def dns_create_record(self, domain: str, host: str, value: str, ipv4=True):
        rrtype = 'A' if ipv4 else 'AAAA'
        res = self._send('dnsAddRecord', domain=domain, rrtype=rrtype, rrhost=host, rrvalue=value)
        return res.findtext('.//reply/detail') == 'success'

    def dns_update_record(self, domain: str):
        pass

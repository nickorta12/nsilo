import os
import aiohttp
import requests
from lxml import etree
from typing import List

# Get apikey from environment
# TODO: Include other methods for this
apikey = os.environ["NSILO_KEY"]

BASEURL = "https://www.namesilo.com/api/"
BASEOPTS = {"version": 1, "type": "xml", "key": apikey}


class NameSiloError(Exception):
    pass


class HostNotFoundError(Exception):
    pass


class DomainInfo:
    def __init__(self, domain: str, resource_record: etree._Element):
        self.domain = domain
        self.id: str = resource_record.findtext("record_id")
        self.type: str = resource_record.findtext("type")
        self.fqn: str = resource_record.findtext("host")
        self.value: str = resource_record.findtext("value")
        self.ttl: str = resource_record.findtext("ttl")
        self.distance: str = resource_record.findtext("distance")

        if domain == self.fqn:
            self.host = ""
        else:
            self.host = self.fqn.replace("." + domain, "")

    def __str__(self):
        obj = {
            "id": self.id,
            "type": self.type,
            "host": self.host,
            "fqn": self.fqn,
            "value": self.value,
            "ttl": self.ttl,
            "distance": self.distance,
        }
        return str(obj)

    def __repr__(self):
        return f'DomainInfo: "{self.fqn} - {self.value}"'


class NameSilo:
    def __init__(self):
        self.session = aiohttp.ClientSession()
        # self.session = requests.session()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.session.close()

    async def _send(self, method: str, **kwargs) -> etree._ElementTree:
        opts = BASEOPTS.copy()
        for key, value in kwargs.items():
            if value is not None:
                opts[key] = value
        async with self.session.get(BASEURL + method, params=opts) as res:
            text = await res.text()
            return etree.fromstring(text)

    async def list_domains(self) -> List[str]:
        """Return list of domains

        :return: List of domains
        :rtype: List[str]
        """

        res = await self._send("listDomains")
        domains = res.xpath("//domain")
        return [x.text for x in domains]

    async def get_domain_info(self, domain: str):
        res = await self._send("getDomainInfo", domain=domain)

    async def dns_list_records(self, domain: str) -> List[DomainInfo]:
        """Gets all dns info for each domain

        :param domain: Domain as returned by list_domains
        :type domain: str
        :return: List of DomainInfo
        :rtype: List[DomainInfo]
        """

        res = await self._send("dnsListRecords", domain=domain)
        records = res.xpath(".//resource_record")
        return [DomainInfo(domain, x) for x in records]

    async def dns_delete_record(self, domain: str, id: str):
        res = await self._send("dnsDeleteRecord", domain=domain, rrid=id)
        code = res.findtext(".//code")
        result = res.findtext(".//detail")
        if code != "300" or result != "success":
            raise NameSiloError(f"Result code of {code} and result of {result}")

    async def dns_add_record(self, domain: str, host: str, value: str, ipv4=True):
        rrtype = "A" if ipv4 else "AAAA"
        res = await self._send(
            "dnsAddRecord", domain=domain, rrtype=rrtype, rrhost=host, rrvalue=value
        )
        return res.findtext(".//reply/detail") == "success"

    async def _dns_get_id(self, domain, host):
        records = await self.dns_list_records(domain)
        for record in records:
            if record.host == host:
                return record.id
        else:
            raise HostNotFoundError(host)

    async def dns_update_record(
        self, domain: str, value: str, host=None, dns_id=None, ipv4=True
    ):
        print("Updating", domain, dns_id)
        rrtype = "A" if ipv4 else "AAAA"
        if dns_id is None and host is None:
            raise ValueError("dns_id and host both can't be None")
        res = await self._send(
            "dnsUpdateRecord",
            domain=domain,
            rrtype=rrtype,
            rrhost=host,
            rrvalue=value,
            rrid=dns_id,
        )
        print("Done", domain, dns_id)
        return res

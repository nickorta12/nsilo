import asyncio
import ipaddress
from argparse import ArgumentParser
from nsilo import NameSilo, DomainInfo
from typing import List


async def _update_domain(api: NameSilo, domain: str, ip: str):
    records: List[DomainInfo] = await api.dns_list_records(domain)
    tasks = []
    for record in records:
        tasks.append(
            api.dns_update_record(domain, ip, dns_id=record.id, host=record.host)
        )
    if len(tasks) > 0:
        await asyncio.wait(tasks)


async def run(ip):
    async with NameSilo() as api:
        domains = await api.list_domains()
        tasks = [_update_domain(api, d, ip) for d in domains]
        await asyncio.wait(tasks)


if __name__ == "__main__":
    parser = ArgumentParser("nsilo-update")
    parser.add_argument("ip", help="New IP Address")
    args = parser.parse_args()

    # Quick verification of address
    try:
        ipaddress.IPv4Address(args.ip)
    except Exception as e:
        parser.error(e)
    loop = asyncio.new_event_loop()
    loop.run_until_complete(run(args.ip))

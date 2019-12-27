import asyncio
from prettytable import PrettyTable
from argparse import ArgumentParser
from nsilo import NameSilo, DomainInfo
from typing import List


async def _get_records(api: NameSilo, domain: str) -> List[DomainInfo]:
    return (domain, await api.dns_list_records(domain))


async def run_full():
    async with NameSilo() as api:
        domains = await api.list_domains()
        tasks = (_get_records(api, d) for d in domains)
        results = await asyncio.gather(*tasks)
    results.sort()
    for domain, records in results:
        print(domain)
        t = PrettyTable(["Host", "IP"])
        for record in records:
            record: DomainInfo
            t.add_row([record.fqn, record.value])
        print(t)

async def run_single(host):
    hparts = host.split(".")
    domain = ".".join(hparts[-2:])
    hostname = ".".join(hparts[:-2])
    async with NameSilo() as api:
        records = await api.dns_list_records(domain)
        for record in records:
            if record.host == hostname:
                print(record.value)
                break

if __name__ == "__main__":
    parser = ArgumentParser("nsilo-get", description="Gets ip addresses for account")
    parser.add_argument("-d", "--domain", help="Specific domain to check")
    args = parser.parse_args()
    loop = asyncio.new_event_loop()

    if args.domain is not None:
        job = run_single(args.domain)
    else:
        job = run_full()

    loop.run_until_complete(job)

import sys
print(sys.path)
from nsilo import NameSilo

def test_domains_are_list():
    nsilo = NameSilo()
    assert type(nsilo.list_domains()) is list

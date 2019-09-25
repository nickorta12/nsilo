import pytest
from nsilo import NSilo

def test_domains_are_list():
    nsilo = NSilo()
    assert type(nsilo.list_domains()) is list
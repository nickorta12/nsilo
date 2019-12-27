from setuptools import setup, find_packages

version = "0.1.0"

setup(
    name="nsilo",
    description="NameSilo interface",
    version=version,
    author="Nicholas Orta",
    author_email="nickorta12@gmail.com",
    packages=find_packages(),
    install_requires=["lxml", "requests", "aiohttp", "PrettyTable"],
)

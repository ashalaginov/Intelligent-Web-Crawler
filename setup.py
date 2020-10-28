__author__ = "Andrii Shalaginov"
__date__ = "$04.okt.2020 10:45:25$"

from setuptools import setup, find_packages


with open("requirements.txt") as f:
    requirements = f.read().splitlines()


setup(
    name="WebCrawler",
    version="0.1",
    packages=find_packages(),
    # Declare your packages' dependencies here, for eg:
    # install_requires=['foo>=3'],
    install_requires=requirements,
    # Fill in these to make your Egg ready for upload to
    # PyPI
    author="Andrii Shalaginov",
    author_email="andrii.shalaginov@gmail.com",
    url="",
    license="",
    long_description="Long description of the crawler",
    # could also include long_description, download_url, classifiers, etc.
)

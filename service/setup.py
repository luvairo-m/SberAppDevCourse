import sys
from setuptools import setup, find_packages

NAME = "openapi_server"
VERSION = "1.0.0"

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = [
    "connexion[flask,swagger-ui,uvicorn]>=3.3.0,<4.0.0",
    "swagger-ui-bundle>=1.1.0",
    "Flask>=2.2.0,<4.0.0",
    "python_dateutil>=2.6.0"
]

setup(
    name=NAME,
    version=VERSION,
    description="API автомастерской",
    author_email="",
    url="",
    keywords=["OpenAPI", "API автомастерской"],
    install_requires=REQUIRES,
    packages=find_packages(),
    package_data={'': ['openapi/openapi.yaml']},
    include_package_data=True,
    entry_points={
        'console_scripts': ['openapi_server=openapi_server.__main__:main']},
    long_description="""\
    API для ведения заказ-нарядов на ремонт автомобилей.
    """
)

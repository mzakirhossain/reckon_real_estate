from setuptools import setup, find_packages

from reckon_real_estate import __version__

setup(
    name="reckon_real_estate",
    version=__version__,
    description="Real Estate vertical for Frappe/ERPNext",
    author="Reckon Technologies Ltd.",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)

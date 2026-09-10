from setuptools import setup, find_packages

setup(
    name="aa-discordvoice-snapshots",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "allianceauth>=5.2.0",
    ],
)

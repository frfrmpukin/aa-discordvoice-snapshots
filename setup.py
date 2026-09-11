from setuptools import setup, find_packages

setup(
    name="aa-discord-voicesnapshot",
    version="1.0.0",
    description="Alliance Auth module for recording and managing Discord voice channel snapshots.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",

    url="https://github.com/frfrmpukin/aa-discord-voicesnapshot",
    project_urls={
        "Source": "https://github.com/frfrmpukin/aa-discord-voicesnapshot",
        "Tracker": "https://github.com/frfrmpukin/aa-discord-voicesnapshot/issues",
    },

    packages=find_packages(),
    include_package_data=True,

    install_requires=[
        "allianceauth>=3.0.0",
        "django>=3.2",
    ],

    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

    python_requires=">=3.8",
)

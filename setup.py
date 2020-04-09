import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="animal-crossing-discord-chanko08",
    version="0.0.3",
    author="Alex Bechanko",
    author_email="chanko08@gmail.com",
    description="Animal Crossing New Horizons Discord bot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chanko08/animal-crossing-turnip-prices",
    packages=setuptools.find_namespace_packages(include="animal_crossing.*"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
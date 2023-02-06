import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="petkitaio",
    version="0.1.0",
    author="Robert Drinovac",
    author_email="unlisted@gmail.com",
    description="Asynchronous Python library for PetKit's API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/RobertD502/petkitaio',
    keywords='petkit, eversweet 3 pro, feeder mini, d4, petkit feeder, petkit water fountain, freshelement solo',
    packages=setuptools.find_packages(),
    python_requires= ">=3.7",
    install_requires=[
        "aiohttp>=3.8.1",
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ),
    project_urls={  # Optional
    'Bug Reports': 'https://github.com/RobertD502/petkitaio/issues',
    'Source': 'https://github.com/RobertD502/petkitaio/',
    },
)

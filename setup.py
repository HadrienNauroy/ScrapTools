import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ScrapTools",
    version="0.0.1",
    author="Hadrien Nauroy",
    author_email="hadriennauroy@gmail.com",
    description="Useful tools for scraping with Selenium",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HadrienNauroy",
    project_urls={
        "Bug Tracker": "https://github.com/HadrienNauroy/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)

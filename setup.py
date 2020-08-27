import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dkextract", # Replace with your own username
    version="1.0",
    author="Carlos Limardo",
    author_email="climardo@gmail.com",
    description="A tool to get certain data from DraftKings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/climardo/dkextract",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
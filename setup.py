import re
from os.path import dirname, join
from setuptools import find_packages, setup

with open(join(dirname(__file__), "projects", "__init__.py")) as fp:
    for line in fp:
        m = re.search(r'^\s*__version__\s*=\s*([\'"])([^\'"]+)\1\s*$', line)
        if m:
            version = m.group(2)
            break
    else:
        raise RuntimeError("Unable to find own __version__ string")

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

extras = {
    "testing": [
        "pytest>=4.4.0",
        "pytest-xdist==1.31.0",
        "pytest-cov==2.8.1",
        "flake8==3.7.9",
        "papermill[s3]==2.1.1",
        "scikit-learn==0.22.2.post1",
        "category-encoders==2.2.2",
        "smac>=0.12,<0.13",
        "auto-sklearn==0.7.0",
        "networkx==2.4",
        "matplotlib==3.3.0"
    ]
}

setup(
    name="projects",
    version=version,
    author="Fabio Beranizo Lopes",
    author_email="fabio.beranizo@gmail.com",
    description="Manages projects.",
    license="Apache",
    url="https://github.com/platiagro/projects",
    packages=find_packages(),
    package_data={
        "projects": ["config/*.ipynb"],
    },
    install_requires=requirements,
    extras_require=extras,
    python_requires=">=3.6.0",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    entry_points={
        "console_scripts": [
            "platiagro-init-db = projects.database:init_db",
        ]
    },
)

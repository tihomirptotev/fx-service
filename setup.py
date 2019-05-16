from setuptools import find_packages, setup

setup(
    name="fx_service",
    version="0.1",
    py_modules=["fx_service"],
    install_requires=[
        "redis",
        "rx==3.0.0b1",
        "psycopg2-binary",
        "sqlalchemy",
        "requests",
        "requests_html",
        "pendulum",
        "loguru",
        "environs",
    ],
    packages=find_packages("."),
    package_dir={"": "."},
    entry_points={"console_scripts": []},
)

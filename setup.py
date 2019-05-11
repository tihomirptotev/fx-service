from setuptools import find_packages, setup

setup(
    name="fx_service",
    version="0.1",
    py_modules=["fx_service"],
    install_requires=[
        "aioredis",
        "asyncpg",
        "databases",
        "mode",
        "requests_html",
        "requests_async",
        "pendulum",
    ],
    packages=find_packages("."),
    package_dir={"": "."},
    entry_points={"console_scripts": []},
)

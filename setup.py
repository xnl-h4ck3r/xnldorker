#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="xnldorker",
    packages=find_packages(),
    version=__import__('xnldorker').__version__,
    description="Run a dork on different search sites",
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    author="@xnl-h4ck3r",
    url="https://github.com/xnl-h4ck3r/xnldorker",
    zip_safe=False,
    install_requires=["termcolor", "requests", "asyncio", "beautifulsoup4", "playwright", "tldextract", "urllib3"],
    entry_points={
        'console_scripts': [
            'xnldorker = xnldorker.xnldorker:main',
        ],
    },
)

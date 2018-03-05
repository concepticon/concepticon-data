from setuptools import setup, find_packages


setup(
    name='pyconcepticon',
    version='1.3.0',
    description='programmatic access to concepticon-data',
    long_description='',
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
    ],
    author='',
    author_email='forkel@shh.mpg.de',
    url='',
    keywords='data linguistics',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'csvw',
        'clldutils>=2.1.0',
        'bibtexparser',
        'tabulate',
        'attrs',
        'cdstarcat',
    ],
    extras_require={
        'dev': [
            'tox',
            'flake8',
            'wheel',
            'twine',
        ],
        'test': [
            'mock',
            'pytest>=3.1',
            'pytest-mock',
            'pytest-cov',
            'coverage>=4.2',
        ],
    },
    entry_points={
        'console_scripts': [
            'concepticon=pyconcepticon.__main__:main',
        ]
    },
    test_suite="pyconcepticon")

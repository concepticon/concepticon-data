from setuptools import setup, find_packages


requires = [
    'clldutils>=0.2',
    'clld'
]

setup(
    name='concepticondata',
    version='0.0',
    description='data for the concepticon site',
    long_description='',
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
    ],
    author='',
    author_email='',
    url='',
    keywords='data linguistics',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    entry_points={
        'console_scripts': [
            'linkconcepts=concepticondata.commands:link',
            'conceptliststats=concepticondata.commands:stats',
        ]
    },
    tests_require=['clld'],
    test_suite="concepticondata")

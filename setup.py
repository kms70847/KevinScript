from setuptools import setup, find_packages

setup(
    name='KevinScript',
    version='1.0.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'kevinscript=ks:main'
        ]
    }
)

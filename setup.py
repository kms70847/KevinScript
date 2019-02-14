from setuptools import setup, find_packages

setup(
    name='KevinScript',
    version='1.0.0',
    packages=find_packages(),
    data_files=[('ks', ['ks/language.txt', 'ks/tokens.txt', 'ks/native_builtin_initialization.k'])],
    entry_points={
        'console_scripts': [
            'kevinscript=ks:main'
        ]
    }
)

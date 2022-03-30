# -*- coding: utf-8 -*-
"""
    vault-dump-restore
    ~~~~~~~~~~~~~~~~~~

    Setup script for packaging and installing vault-dump-restore
"""
import pathlib
from setuptools import setup, find_packages

this_directory = pathlib.Path(__file__).parent.resolve()
long_description = (this_directory / 'README.md').read_text(encoding='utf-8')

setup(
    name="vault-dump-restore",
    version='0.5.1',
    description='Dumps keys from a Hashicorp Vault instance to be able to restore it on another instance',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Hugo Cisneiros (Eitch)',
    author_email='hugo.cisneiros@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='hashicorp, vault, keys, secrets, backup, restore',
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6, <4",
    install_requires=[
        'hvac==0.11.2'
    ],
    entry_points={
        'console_scripts': [
            'vault-dump=vault_dump_restore.cli:dump',
            'vault-restore=vault_dump_restore.cli:restore'
        ],
    },
)

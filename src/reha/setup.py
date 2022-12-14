from setuptools import setup


setup(
    name='reha',
    install_requires=[
    'pymongo',
    'orjson',
    'horseman',
    'knappe',
    'knappe_deform',
    'pydantic[email]',
    ],
    extras_require={
        'test': [
            'pytest',
            'pyhamcrest',
            'pytest-mongodb'
        ]
    }
)

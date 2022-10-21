from setuptools import setup


setup(
    name='backend',
    install_requires=[
        'reha',
    ],
    extras_require={
        'test': [
            'pytest',
            'pyhamcrest',
            'pytest-mongodb'
        ]
    }
)

from setuptools import setup, find_packages

setup(
    name='alerttrack',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'streamlit',
        'requests',
        'beautifulsoup4',
    ],
    entry_points={
        'console_scripts': [
            'alerttrack-run = main:run',
        ],
    },
    python_requires='>=3.7',
)

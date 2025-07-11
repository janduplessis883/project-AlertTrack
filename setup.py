from setuptools import setup, find_packages

setup(
    name='streamlit-web-scraper',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'streamlit',
        'requests',
        'beautifulsoup4',
    ],
    entry_points={
        'console_scripts': [
            'streamlit-web-scraper = streamlit_app.app:main',
        ],
    },
    python_requires='>=3.7',
)

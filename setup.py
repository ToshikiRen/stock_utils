from setuptools import setup, find_packages

setup(
    name="stock_utils",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'yfinance',
        'pandas',
        'matplotlib'
    ],
)

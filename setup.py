from setuptools import setup, find_packages

setup(
    name='md2notion',
    version='0.1',
    author='Omar Shalash',
    packages=find_packages(where="."),
    description='A utility for converting Markdown to Notion',
    python_requires='>=3.6'
)

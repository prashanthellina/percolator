from setuptools import setup, find_packages

setup(
    name="percolator",
    version='0.1',
    description="Performs inverse of document search",
    keywords='percolator',
    author='Prashanth Ellina',
    author_email="Use the github issues",
    url="https://github.com/prashanthellina/percolator",
    license='MIT License',
    install_requires=[
        'whoosh',
    ],
    package_dir={'percolator': 'percolator'},
    packages=find_packages('.'),
    include_package_data=True
)

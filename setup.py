from setuptools import setup, find_packages

setup(
    name='pywebcoos',
    version='0.1.1',
    description='Python wrapper for the WebCOOS API.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['idna', 'numpy', 'pandas', 'pytest', 'pytz', 'requests']
)

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# Get version number
from geotrigger.version import VERSION

readme = open('README.md')

setup(
    name='geotrigger-python',
    version=VERSION,
    description='A simple client library for interacting with the ArcGIS Geotrigger API.',
    long_description=readme.read(),
    author='Josh Yaganeh',
    author_email='jyaganeh@esri.com',
    url='https://github.com/esri/geotrigger-python',
    packages=['geotrigger',],
    classifiers=[
        'Development Status :: 4 - Beta', # 4 Beta, 5 Production/Stable
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)
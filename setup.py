from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup
from tornadio2go import NAME, VERSION

setup(
    name=NAME,
    version=VERSION,
    author='Nimrod A. Abing',
    author_email='nimrod.abing@gmail.com',
    packages=['tornadio2go', 'tornadio2go.management', 'tornadio2go.management.commands'],
    url='https://github.com/rudeb0t/tornadio2go',
    license='LICENSE.txt',
    description='Seamlessly run your Django and TornadIO2 project inside Tornado. Like.A.Boss.',
    long_description=open('README.rst').read(),
    install_requires=[
        'Django >= 1.4.0',
        'TornadIO2 >= 0.0.4'
    ]
)

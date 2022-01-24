from setuptools import setup

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
   name='ptp-optimization',
   version='1.0',
   description='Precision Time Protocol Optimization',
   license="GPL-2.0-or-later",
   long_description=long_description,
   author='Maciej Machnikowski',
   author_email='maciej.machnikowski@intel.com',
   url="https://netdevconf.info/0x15/session.html?Precision-Time-Protocol-optimization-using-genetic-algorithm",
   packages=['ptp-optimization'],
   install_requires=['numpy', 'scikit-learn', 'matplotlib', 'eval'],
   scripts=[
            'evaluate.py',
            'main.py',
            'parse_ptp.py',
           ]
)

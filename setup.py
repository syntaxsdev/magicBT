from setuptools import setup, find_packages

setup(
  name="magicBT",
  version="0.0.2",
  packages=find_packages(include=['magicBT', 'magicBT.*']),
  install_requires=[
      'pydantic>=2.7.4',
      'numpy>=2.0.0',
      'twelvedata>=1.2.12',
      'influxdb==1.43.0'
      ]
)
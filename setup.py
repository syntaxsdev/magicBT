from setuptools import setup, find_packages

setup(
  name="magicBT",
  version="0.0.1",
  packages=find_packages(include=['magicBT', 'magic.*']),
  install_requires=[
      'pydantic>=2.7.4',
      'numpy>=2.0.0',
      'twelvedata>=1.2.12'
      ]
)
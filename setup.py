from setuptools import setup

setup(name='hypergraphs',
      author='Tim Vieira',
      description='Reference implementation of algorithms for hypergraphs.',
      version='1.0',
      install_requires=[
          'arsenal',
          'nltk',
          'numpy',
          'pandas',
          'semirings @ git+https://github.com/timvieira/semirings',
      ],
      dependency_links=[
          'https://github.com/timvieira/arsenal.git',
      ],
      packages=['hypergraphs'],
)

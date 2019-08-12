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
      ],
      dependency_links=[
          'https://github.com/timvieira/arsenal.git',
      ],
      packages=['hypergraphs'],
)

import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

requires = ('voteit.core',)

setup(name='voteit.dutt',
      version='0.1',
      description='voteit.dutt',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Robin Harms Oredsson',
      author_email='robin@betahaus.net',
      url='',
      keywords='web pyramid pylons voteit',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="voteit.dutt",
      entry_points = """\
      [fanstatic.libraries]
      voteit_dutt_lib = voteit.dutt.fanstaticlib:voteit_dutt_lib
      """,
      paster_plugins=['pyramid'],
      message_extractors = { '.': [
              ('**.py',   'lingua_python', None ),
              ('**.pt',   'lingua_xml', None ),
              ('**.zcml',   'lingua_zcml', None ),
              ]},
      )


from setuptools import setup, find_packages
import os

version = '0.3dev'

setup(name='gdw.stats',
      version=version,
      description="GDW Stats",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Jean Francois Roche',
      author_email='jfroche@affinitic.be',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['gdw'],
      include_package_data=True,
      zip_safe=False,
      extras_require=dict(
            test=['zope.testing', 'mockito', 'psycopg2', 'plone.app.testing', 'lxml']),
      entry_points={
            'console_scripts': [
                'gdwstats = gdw.stats.cmdline:main',
                'log2db = gdw.stats.scripts.log2db:main']},
      install_requires=[
          'setuptools',
          'Zope2',
          'z3c.form',
          'z3c.autoinclude',
          'affinitic.db',
          'gites.db',
          'dateutil',
          'grokcore.component',
          'five.grok',
          'psycopg2',
          'plone.z3cform',
          'plone.memoize',
          'Plone',
          'PIL',
          'plone.app.z3cform',
          'sqlalchemy',
          'apachelog'])

from setuptools import setup, find_packages
import os

version = open(os.path.join("collective",
                            "multimodeview",
                            "version.txt")).read().strip()

setup(name='collective.multimodeview',
      version=version,
      description="Simple package to manage views with multiple modes.",
      long_description=(open("README.txt").read() + "\n" +
                        open(os.path.join("collective",
                                          "multimodeview",
                                          "HISTORY.txt")).read()),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Framework :: Plone",
          "Programming Language :: Python",
          ],
      keywords='multimode view',
      author='Zest Software',
      author_email='info@zestsoftware.nl',
      url='https://github.com/zestsoftware/collective.multimodeview',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )

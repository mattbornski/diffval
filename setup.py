import setuptools
import glob
import os.path

if __name__ == '__main__':
    # Define a Python extension.
    extension = [
      'diffval.interface',
      'diffval.idlval',
      'diffval.pyval',
      'diffval.log',
      'diffval.session',
      'diffval.test',
    ]

    # Invoke the setup code, which will (depending on the command line
    # arguments) build, install, or otherwise tinker with this package
    # on this system.
    setuptools.setup(
      name = 'diffval',
      version = '0.11',
      description = 'Validates tests by comparing real output ' \
        + 'against expected output',
      author = 'Matt Born',
      author_email = 'mattborn@ssl.berkeley.edu',
      url = 'http://efw.ssl.berkeley.edu/packages/diffval',
      classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Testing',
      ],
      py_modules = extension,
      entry_points = """
        [console_scripts]
        diffval = diffval.interface:main
      """,
    )

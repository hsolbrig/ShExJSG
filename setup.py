import sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.version_info < (3, 6):
    print("This module requires python 3.6 or later")
    sys.exit(1)

setup(
    name='ShExJSG',
    version='0.5.1',
    packages=['ShExJSG'],
    url="http://github.com/hsolbrig/ShExJSG",
    license='Apache 2.0',
    author='Harold Solbrig',
    author_email='solbrig@solbrig-informatics.com',
    description='"ShExJSG - Astract Syntax Tree for the ShEx 2.0 language',
    install_requires=['PyJSG>=0.9.0', 'PyShExC>=0.5.0'],
    tests_require = ['yadict-compare>=1.2.0', 'requests>=2.19', 'jsonasobj>=1.2.1'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Compilers',
        'Programming Language :: Python :: 3.6']
)

import sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.version < (3, 6):
    print("This module requires python 3.6 or later")
    sys.exit(1)

# This module currently works with python3.6 or later
with open('requirements.txt') as reqs:
    requires = [l for l in reqs.readline()]

setup(
    name='ShExJSG',
    version='0.1.0',
    packages=['ShExJSG'],
    url="http://github.com/hsolbrig/ShExJSG",
    license='Apache 2.0',
    author='Harold Solbrig',
    author_email='solbrig@solbrig-informatics.com',
    description='"ShExJSG - Astract Syntax Tree for the ShEx 2.0 language',
    install_requires=requires,
    tests_require = ['yadict-compare', 'requests'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Compilers',
        'Programming Language :: Python :: 3 :: Only']
)

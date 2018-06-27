from setuptools import setup
import re

VERSIONFILE="fineDi/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

setup(
    name='fineDi',
    packages=['fineDi'],
    include_package_data=True,
    install_requires=[
        'flask',
        'ipdb',
        'numpy',
    ],
)

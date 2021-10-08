import os
import re
from setuptools import find_packages, setup

# read in README
this_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_dir, 'README.md'), 'rb') as f:
    long_description = f.read().decode().strip()

# load version
with open("hop_comms/_version.py", "r") as f:
    version_file = f.read()
version_match = re.search(r"^version = ['\"]([^'\"]*)['\"]", version_file, re.M)
version = version_match.group(1)

# requirements
install_requires = [
    "hop-client >= 0.3",
    "hop-plugin-snews",
    "jsonschema",
    "numpy",
    "pymongo",
    "python-dotenv",
]


def read_requirements():
    # with open('hop_comms/requirements.txt') as req:
    #     content = req.read()
    #     requirements = content.split('\n')
    # return install_requires.append(requirements)
    return install_requires


extras_require = {
    'dev': [
        'autopep8',
        'flake8',
        'mongomock',
        'pytest >= 5.0, < 5.4',
        'pytest-console-scripts',
        'pytest-cov',
        'pytest-mongodb',
        'pytest-runner',
        'twine',
    ],
    'docs': [
        'sphinx',
        'sphinx_rtd_theme',
        'sphinxcontrib-programoutput'
    ],
}

setup(
    name='hop_comms',
    version=version,
    description='An alert application for observing supernovas.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/RiceAstroparticleLab/hop-SNalert-app.git',
    author='Skylar(Yiyang) Xu, Patrick Godwin, Bryce Cousins',
    author_email='yx48@rice.edu/skyxuyy@gmail.com, patrick.godwin@psu.edu, bfc5288@psu.edu',
    license='BSD 3-Clause',
    setup_requires=['pbr'],
    pbr=True,
    packages=find_packages(),
    include_package_data=True,

    entry_points={
        'console_scripts': [
            'hop_comms = hop_comms.__main__:main',
        ],
    },

    python_requires='>=3.6.*',
    install_requires=read_requirements(),
    extras_require=extras_require,

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Astronomy',
        'Topic :: Scientific/Engineering :: Physics',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: MacOS',
        'License :: OSI Approved :: BSD License',
    ],

)

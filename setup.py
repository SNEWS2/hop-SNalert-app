import os
from setuptools import setup

# read in README
this_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_dir, 'README.md'), 'rb') as f:
    long_description = f.read().decode().strip()

# requirements
install_requires = [
    "hop-client >= 0.1",
    "dataclasses-jsonschema",
    "numpy",
    "pymongo",
    "python-dotenv",
]
extras_require = {
    'dev': ['pytest', 'pytest-console-scripts', 'pytest-cov', 'flake8', 'flake8-black'],
    'docs': ['sphinx', 'sphinx_rtd_theme', 'sphinxcontrib-programoutput'],
}

setup(
    name = 'hop-SNalert-app',
    description = 'An alert application for observing supernovas.',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    url = 'https://github.com/RiceAstroparticleLab/hop-SNalert-app.git',
    author = 'Skylar(Yiyang) Xu, Patrick Godwin, Bryce Cousins',
    author_email = 'yx48@rice.edu/skyxuyy@gmail.com, patrick.godwin@psu.edu, bfc5288@psu.edu',
    license = 'BSD 3-Clause',

    packages = ['hop.apps.SNalert', 'hop.apps.SNalert.dataPacket'],

    entry_points = {
        'console_scripts': [
            'SNalert = hop.apps.SNalert.__main__:main',
        ],
        'hop_plugin': ["observationMsg-plugin = hop.apps.SNalert.plugins"]
    },

    python_requires = '>=3.6.*',
    install_requires = install_requires,
    extras_require = extras_require,

    classifiers = [
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

from setuptools import setup, find_packages

setup(
    name="uglypty",
    version="0.8.16",
    description="UglyPTY - A PyQt6-based SSH, Mapping and Automation Tooling.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author="Scott Peterman",
    author_email="scottpeterman@gmail.com",
    url="https://github.com/scottpeterman/UglyPTY", 
    license="GPLv3",
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=['asttokens==2.2.1',
                     'backcall==0.2.0',
                     'bcrypt==4.0.1',
                     'cached-property==1.5.2',
                     'certifi==2023.7.22',
                     'cffi==1.15.1',
                     'charset-normalizer==3.2.0',
                     'click==8.1.3',
                     'colorama==0.4.6',
                     'crayons==0.4.0',
                     'cryptography==41.0.1',
                     'darkdetect==0.7.1',
                     'decorator==5.1.1',
                    'diff-match-patch==20230430',
                     'executing==1.2.0',
                     'future==0.18.3',
                     'greenlet==2.0.2',
                     'idle==1.0.4',
                     'idna==3.4',
                     'igraph==0.10.6',
                     'inflection==0.5.1',
                     'jedi==0.19.0',
                     'Jinja2==3.1.2',
                     'jmespath==1.0.1',
                      'ldap3==2.9.1',
                     'MarkupSafe==2.1.3',
                     'matplotlib-inline==0.1.6',
                     'mypy-extensions==1.0.0',
                      "netmiko==3.3.3",
                     'numpy==1.25.2',
                     'n2g==0.3.3',
                     'pandas==2.0.3',
                     'pandasql==0.7.3',
                     'paramiko==3.2.0',
                     'parso==0.8.3',
                     'pickleshare==0.7.5',
                     'prompt-toolkit==3.0.39',
                     'pure-eval==0.2.2',
                     'pycparser==2.21',
                     'pycryptodome==3.18.0',
                     'Pygments==2.16.1',
                     'PyNaCl==1.5.0',
                     'PyQt6==6.5.1',
                     'PyQt6-Qt6==6.5.1',
                     'PyQt6-sip==13.5.1',
                     'PyQt6-WebEngine==6.5.0',
                     'PyQt6-WebEngine-Qt6==6.5.1',
                     'pyqtdarktheme==2.1.0',
                     'pyserial==3.5',
                     'python-dateutil==2.8.2',
                     'python-igraph==0.10.6',
                     'pytz==2023.3',
                      'pynetbox==7.2.0',
                     'PyYAML==6.0.1',
                     'qt-material==2.14',
                     'requests==2.31.0',
                     'scp==0.14.5',
                     'six==1.16.0',
                     'SQLAlchemy==2.0.20',
                     'sqlalchemy-orm==1.2.10',
                     'SQLAlchemy-serializer==1.4.1',
                     'stack-data==0.6.2',
                     'svgwrite==1.4.3',
                     'textfsm==1.1.3',
                     'texttable==1.6.7',
                     'tomli==2.0.1',
                     'tqdm==4.66.1',
                    'tftpy==0.8.2',
                      'ttp==0.9.5',
                     'traitlets==5.9.0',
                     'typing-inspect==0.9.0',
                     'typing_extensions==4.7.1',
                     'tzdata==2023.3',
                     'urllib3==2.0.4',
                     'wcwidth==0.2.6'],
    #
    #
# scripts=['uglypty/uglypty.py'],
    package_data={
        'uglypty': [
             'icons/*',
        'Library/*',
        'logs/*',
        'static/*',
        'static/images/*',
        'sessions/*',
        'uglyplugin_serial/*',
        '*.html'

        ],
    },
    python_requires='>=3.9',
)

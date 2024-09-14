from setuptools import setup, find_packages

setup(
    name='unrealircd_rpc_py',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.1"
    ],
    author='adator',
    author_email='debian@deb.biz.st',
    description='Python library for unrealIRCD json-rpc',
    long_description=open('README.MD').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/adator85/unrealircd_rpc_py',
    package_data={
        '': ['README.MD'],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    python_requires='>=3.10'
)
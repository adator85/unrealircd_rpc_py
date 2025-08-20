from setuptools import setup, find_packages

setup(
    name='unrealircd_rpc_py',
    version='2.0.3',
    packages=find_packages(exclude=["tests","test_*"]),
    install_requires=[
        "requests>=2.25.1",
        "websockets>=13.1"
    ],
    author='adator',
    author_email='debian@deb.biz.st',
    description='Python library for UnrealIRCd json-rpc',
    long_description=open('README.MD').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/adator85/unrealircd_rpc_py',
    package_data={
        '': ['README.MD'],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    keywords="Unrealircd, irc, jsonrpc, json-rpc, ircd",
    python_requires='>=3.10'
)
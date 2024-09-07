# UNREALIRCD-RPC-PY
![Static Badge](https://img.shields.io/badge/UnrealIRCd-6.2.2%20or%20later-green)
![Static Badge](https://img.shields.io/badge/Python3-3.10%20or%20later-green)
![Dynamic JSON Badge](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fadator85%2Funrealircd_rpc_py%2Fmain%2Fversion.json&query=version&label=Current%20Version)
![Static Badge](https://img.shields.io/badge/Maintained-Yes-green)


#### If you are using Python3, this package can help you to parse all json responses it does all the work for you.

## How to use this package

    $ pip3 install unrealircd_rpc_py

## How to work with

This package allows easy interfacing with UnrealIRCd through regular Python3 code, such as:

        from unrealircd_rpc_py.Loader import Loader

        # Initialize your connexion to unrealircd
        rpc = Loader(
                req_method='requests', # you can also use 'socket'
                url='https://your.irc.domaine.org:8600/api',
                endpoint='api',
                host='your.irc.domaine.org',
                port=8600,
                username='apiname',
                password='apiPASSWORD',
                debug_level=10
            )

        # Enjoy the power of JSON-RPC

        User = rpc.User
        response = User.get('adator')

        print(f'Nickname: {response.name}')
        print(f'Ip: {response.ip}')

        Channels = rpc.Channel
        response = Channels.list_(_object_detail_level=3)

        for chan in Channels.DB_CHANNELS:
            if chan.name == '#welcome':
                print(f'Channel: {chan.name}')
                print(f'Created on: {chan.creation_time}')
                print(f'Bans: {chan.bans}')
                print(f'Members: {chan.members}')


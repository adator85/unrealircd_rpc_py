# UNREALIRCD-RPC-PY
![Static Badge](https://img.shields.io/badge/UnrealIRCd-6.2.2%20or%20later-green)
![Static Badge](https://img.shields.io/badge/Python3-3.10%20or%20later-green)
![Dynamic JSON Badge](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fadator85%2Funrealircd_rpc_py%2Fmain%2Fversion.json&query=version&label=Current%20Version)
![Static Badge](https://img.shields.io/badge/Maintained-Yes-green)


## Introduction
If you are using Python3, this package can help you to parse all json responses it does all the work for you.

## How to install this package
```bash
    pip3 install unrealircd_rpc_py
```
> [!NOTE]
> I recommend installing a virtual environment and then installing the package within it.

## How to establish the link
```python
    # Using requests method
    rpc = Loader(
            req_method='requests',
            url='https://your.irc.domaine.org:8600/api',
            username='apiname',
            password='apiPASSWORD'
        )

    # Using socket method
    rpc = Loader(
            req_method='socket',
            url='https://your.irc.domaine.org:8600/api',
            username='apiname',
            password='apiPASSWORD'
        )

    # Using unixsocket method (Local only)
    rpc = Loader(
            req_method='unixsocket',
            path_to_socket_file='/path/to/unrealircd/data/rpc.socket'
        )

    # Live Connection (Local only)
    LiveRpc = Live(
        path_to_socket_file='/path/to/unrealircd/data/rpc.socket',
        callback_object_instance=Callback_class_instance,
        callback_method_name='your_method_name'
    )

```

## How to work with (remotly)

This package allows easy interfacing with UnrealIRCd through regular Python3 code, such as:
```python
    from unrealircd_rpc_py.Loader import Loader

    # Initialize your connexion to unrealircd
    rpc = Loader(
            req_method='requests', # you can also use 'socket'
            url='https://your.irc.domaine.org:8600/api',
            username='apiname',
            password='apiPASSWORD'
        )

    # Enjoy the power of JSON-RPC

    User = rpc.User
    response = User.get('adator')

    print(f'Nickname: {response.name}')
    print(f'Ip: {response.ip}')

    Channels = rpc.Channel
    response = Channels.list_(_object_detail_level=3)

    for chan in Channels:
        print(f'-' * 16)
        print(f'Channel: {chan.name}')
        print(f'Created on: {chan.creation_time}')
        print(f'Bans: {chan.bans}')
        print(f'Members: {chan.members}')
        print(f'-' * 16)
```
## How to work with (using unix socket locally)

This package allows easy interfacing with UnrealIRCd through regular Python3 code, such as:
```python
    from unrealircd_rpc_py.Loader import Loader

    # Initialize your connexion to unrealircd
    rpc = Loader(
            req_method='unixsocket',
            path_to_socket_file='/path/to/unrealircd/data/rpc.socket'
        )

    # Enjoy the power of JSON-RPC

    User = rpc.User
    response = User.get('adator')

    print(f'Nickname: {response.name}')
    print(f'Ip: {response.ip}')

    Channels = rpc.Channel
    response = Channels.list_(_object_detail_level=3)

    # The auto completion should help you to find all available attributes
    for chan in Channels:
        print(f'-' * 16)
        print(f'Channel: {chan.name}')
        print(f'Created on: {chan.creation_time}')
        print(f'Bans: {chan.bans}')
        print(f'Members: {chan.members}')
        print(f'-' * 16)
```
## How to work with (using Live unix socket)
```python
    from unrealircd_rpc_py.Live import Live

    # This is un callback class that will recieve the response
    from TestObject import TestObject

    InitCallbackClass = TestObject()

    # The Callback method must always have 1 parameter as string
    liveRpc = Live(
        path_to_socket_file='/path/to/unrealircd/data/rpc.socket',
        callback_object_instance=InitCallbackClass,
        callback_method_name='your_method_name'
    )

    # This method will run forever and will send to your callback method the response
    # in SimpleNameSpace type that you can parse
    liveRpc.subscribe()
```

## Exemple of a Callback Class
```python
    class CallbackObject:

        def __init__(self) -> None:
            pass

        def run(self, json_response) -> bool:

            print(json_response)

            if type(json_response.result) != bool:
                print(json_response.result.channel)
```

## Object that you can use in a synchrone mode
```python
    from unrealircd_rpc_py.Loader import Loader

    # Initialize your connexion to unrealircd using the unixsocket
    rpc = Loader(
            req_method='unixsocket',
            path_to_socket_file='/path/to/unrealircd/data/rpc.socket'
        )

    Channel = rpc.Channel
    Name_ban = rpc.Name_ban
    Server_ban_exception = rpc.Server_ban_exception
    Server_ban = rpc.Server_ban
    Spamfilter = rpc.Spamfilter
    Stats = rpc.Stats
    User = rpc.User
    Whowas = rpc.Whowas
    Log = rpc.Log # This feature requires unrealIRCd 6.1.8 or higher

```

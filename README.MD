# UNREALIRCD-RPC-PY
![Static Badge](https://img.shields.io/badge/UnrealIRCd-6.2.2%20or%20later-green)
![Static Badge](https://img.shields.io/badge/Python3-3.10%20or%20later-green)
![Static Badge](https://img.shields.io/badge/Requests->=2.25.1-green)
![Static Badge](https://img.shields.io/badge/Websockets->=13.1-green)
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
### Using requests module
```python
    from unrealircd_rpc_py.Loader import Loader
    # Using requests method
    rpc = Loader(
            req_method='requests',
            url='https://your.irc.domaine.org:8600/api',
            username='apiname',
            password='apiPASSWORD'
        )
```
### Using socket method
```python
    from unrealircd_rpc_py.Loader import Loader
    # Using socket method
    rpc = Loader(
            req_method='socket',
            url='https://your.irc.domaine.org:8600/api',
            username='apiname',
            password='apiPASSWORD'
        )
```
### Using unixsocket method (Local only)
```python
    from unrealircd_rpc_py.Loader import Loader
    # Using unixsocket method (Local only)
    rpc = Loader(
            req_method='unixsocket',
            path_to_socket_file='/path/to/unrealircd/data/rpc.socket'
        )
```
### Live Connection (Local Only)
```python
    from unrealircd_rpc_py.Live import Live
    # Live Connection (Local only) using unix socket
    LiveRpc = Live(
        req_method='unixsocket',
        path_to_socket_file='/path/to/unrealircd/data/rpc.socket',
        callback_object_instance=Callback_class_instance,
        callback_method_name='your_method_name'
    )
```
### Live connection (Local or Remote)
```python
    from unrealircd_rpc_py.Live import Live
    # Live Connection (Local Or Remote)
    liveRpc = Live(
        req_method='websocket',
        url='https://your.irc.domaine.org:8600/api',
        username='apiname',
        password='apiPASSWORD',
        callback_object_instance=InitCallbackClass,
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
    
    # Handling errors
    if rpc.get_error.code != 0:
        # if code is not 0 then there is an error
        print(f"Your Error Message: {rpc.get_error.message}")
    
    # You can also access errors like so:
    if User.get_error.code != 0:
        print(f"Your Error Message: {User.get_error.message}")

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
## Object that you can use in a synchrone mode
```python
    from unrealircd_rpc_py.Loader import Loader

    # Initialize your connexion to unrealircd using one of the three method
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
# Live Connection via unixsocket or websocket
## How to work with (using Live unixsocket)
```python
    from unrealircd_rpc_py.Live import Live

    # This is un callback class that will recieve the response
    from TestObject import TestObject

    InitCallbackClass = TestObject()

    # The Callback method must always have 1 parameter as string
    liveRpc = Live(req_method='unixsocket',
        path_to_socket_file='/path/to/unrealircd/data/rpc.socket',
        callback_object_instance=InitCallbackClass,
        callback_method_name='your_method_name'
    )

    # This method will run forever and will send to your callback method the response
    # in SimpleNameSpace type that you can parse
    if liveRpc.get_error.code == 0:
        # Subscribe to live events
        liveRpc.subscribe()
    else:
        # If error show the error message
        print(liveRpc.get_error.message)
```
## How to work with (using Live websocket)
```python
    from unrealircd_rpc_py.Live import Live

    # This is un callback class that will recieve the response
    from TestObject import TestObject

    InitCallbackClass = TestObject()

    # The Callback method must always have 1 parameter as string
    liveRpc = Live(req_method='websocket',
        url='https://your.irc.domaine.org:8600/api',
        username='apiname',
        password='apiPASSWORD',
        callback_object_instance=InitCallbackClass,
        callback_method_name='your_method_name'
    )

    # This method will run forever and will send to your callback method the response
    # in SimpleNameSpace type that you can parse
    if liveRpc.get_error.code == 0:
        # Subscribe to live events
        liveRpc.subscribe()
    else:
        # If error show the error message
        print(liveRpc.get_error.message)
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
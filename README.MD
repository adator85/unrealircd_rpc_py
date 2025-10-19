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
    from unrealircd_rpc_py.ConnectionFactory import ConnectionFactory

    # Define your connection string
    connection_string = {
        'url': 'https://your.irc.domaine.org:8600/api',
        'username':'API_USERNAME',
        'password':'API_PASSWORD'
    }

    # Use the factory to create your connection object
    conn = ConnectionFactory().get('http')
    conn.setup(connection_string)
```
### Using unixsocket method (Local only)
```python
    from unrealircd_rpc_py.ConnectionFactory import ConnectionFactory

    # Define your connection string
    connection_string = {
        'path_to_socket_file': '/path/to/unrealircd/data/rpc.socket'
        }

    # Use the factory to create your connection object
    conn = ConnectionFactory().get('unixsocket')
    conn.setup(connection_string)
```

## How to work with it
This package allows easy interfacing with UnrealIRCd through regular Python3 code, such as:
```python
    # Enjoy the power of JSON-RPC
    User = conn.User
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
## Object that you can use in a synchrone mode
```python
    # After connecting using one of the methods listed above.
    rpc = conn
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

### Live Connection using UnixSocket (Local Only)
```python
    from unrealircd_rpc_py.LiveConnectionFactory import LiveConnectionFactory

    # Live Connection (Local only) using unix socket
    liverpc = LiveConnectionFactory().get('unixsocket')
    liverpc.setup({
        'path_to_socket_file': '/path/to/unrealircd/data/rpc.socket',
        'callback_object_instance' : callback_function_instance,
        'callback_method_or_function_name': 'your_method_name'
    })
```
### Live connection using Websocket (Local or Remote)
```python
    from unrealircd_rpc_py.LiveConnectionFactory import LiveConnectionFactory

    # Live Connection (Local Or Remote) using websocket
    liverpc = LiveConnectionFactory().get('http')
    liverpc.setup({
        'url': 'https://your.irc.domaine.org:8600/api',
        'username': 'Your-api-username',
        'password': 'Your-api-password',
        'callback_object_instance' : callback_function_instance,
        'callback_method_or_function_name': 'your_method_name'
    })
```
# Live Connection via unixsocket or websocket
## How to work with
-  Class: see [how_to_use_it_live_class.py](https://github.com/adator85/unrealircd_rpc_py/blob/main/how_to_use_it_live_class.py)
-  Function: see [how_to_use_it_live_func.py](https://github.com/adator85/unrealircd_rpc_py/blob/main/how_to_use_it_live_func.py)
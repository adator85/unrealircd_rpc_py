from unrealircd_rpc_py.ConnectionFactory import ConnectionFactory

try:

    # Init, Setup and connect
    rpc = ConnectionFactory(debug_level=10).get('http')
    check = rpc.setup({
        'url':'https://your.rpc.link:PORT/api',
        'username':'Your-rpc-user',
        'password':'your-rpc-password'
    })
    # If errors it will raise RpcConnectionError

    # Use User object
    Users = rpc.User.list_()

    for u in Users:
        print(u.name, u.hostname, sep=' / ')

    get_user = rpc.User.get('adator')
    print(get_user.name, get_user.hostname, sep=' / ')

    # Use Channel object
    Channels = rpc.Channel.list_()
    for c in Channels:
        print(c.name, c.topic, c.num_users, sep=' / ')

    lkp_chan = rpc.Channel.get('#welcome')
    print(lkp_chan.name, lkp_chan.topic, lkp_chan.num_users, sep=' / ')

    Servers = rpc.Server.module_list('001')
    for server in Servers:
        if server.error.code != 0:
            print(f"{server.error.message} ({server.error.code})")
            break

except AttributeError as ae:
    print(ae)
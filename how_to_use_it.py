from unrealircd_rpc_py.ConnectionFactory import ConnectionFactory

try:

    # Init, Setup and connect
    rpc = ConnectionFactory().get('http')
    check = rpc.setup({
        'url':'https://your.rpc.link:PORT/api',
        'username':'Your-rpc-user',
        'password':'your-rpc-password'
    })
    # If errors it will raise RpcConnectionError

    # Set the issuer:
    rpc.Rpc.set_issuer('rpc_nickname')

    # Use User object
    Users = rpc.User.list_()

    for u in Users:
        print("Connected User:", u.name, u.hostname, sep=' / ')

    get_user = rpc.User.get(nickoruid='adator')
    print("Information about user:", get_user.name, get_user.hostname, sep=' / ')

    # Use Channel object
    Channels = rpc.Channel.list_()
    for c in Channels:
        print("List of channels:", c.name, c.topic, c.num_users, sep=' / ')

    lkp_chan = rpc.Channel.get(channel='#jsonrpc')
    print("Information about specific channel:", lkp_chan.name, lkp_chan.topic, lkp_chan.num_users, sep=' / ')

    Server = rpc.Server.get(serverorsid='001')
    ServerModules = rpc.Server.module_list(serverorsid='001')
    print("Server name:", Server.name, "| Number of modules:", len(ServerModules))

    for server_module in ServerModules:
        if server_module.error.code != 0:
            print(f"{server_module.error.message} ({server_module.error.code})")
            break

except Exception as err:
    print(err)
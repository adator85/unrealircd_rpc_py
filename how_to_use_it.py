from unrealircd_rpc_py.Loader import Loader

try:

    # Init
    rpc = Loader(
            req_method='requests',
            url='https://your.rpc.link:PORT/api',
            username='Your-rpc-user',
            password='your-rpc-password'
        )

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

    Server = rpc.Server.module_list('001')
    if Server is None:
        print(rpc.Server.Error.message)
    else:
        for mod in Server:
            print(mod.name)

except AttributeError as ae:
    rpc.Connection.Logs.error(ae)
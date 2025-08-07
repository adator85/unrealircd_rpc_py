import sys
from unrealircd_rpc_py.Live import LiveWebsocket

##########################################
# How to connect using callback function #
##########################################

def callback_function_irc(response):

    if hasattr(response, 'result'):
        if isinstance(response.result, bool) and response.result:
            # Check if you are allowed to use log endpoint
            print(liverpc.get_error)
            return

    level = response.result.level if hasattr(response.result, 'level') else ''
    subsystem = response.result.subsystem if hasattr(response.result, 'subsystem') else ''
    event_id = response.result.event_id if hasattr(response.result, 'event_id') else ''
    log_source = response.result.log_source if hasattr(response.result, 'log_source') else ''
    msg = response.result.msg if hasattr(response.result, 'msg') else ''

    build_msg = f"{log_source}: [{level}] {subsystem}.{event_id} - {msg}"

    # Check if there is an error
    if liverpc.get_error.code != 0:
        print(f"Your Error message: {liverpc.get_error.message}")

    print(build_msg)

# Init your live stream using websocket
liverpc = LiveWebsocket(
            url="https://your.rpc.link:PORT/api",
            username='Your-rpc-username',
            password='your-rpc-password',
            callback_object_instance=sys.modules[__name__],
            callback_method_or_function_name='callback_function_irc'
        )

# Check if connection is correct
if liverpc.get_error.code != 0:
    print(liverpc.get_error.message, liverpc.get_error.code)
    sys.exit(1)

liverpc.subscribe(["all"])

########################################
# How to connect using callback method #
########################################

class CallBack:

    def __init__(self):

        self.liverpc: LiveWebsocket = LiveWebsocket(
            url="https://your.rpc.link:PORT/api",
            username='Your-rpc-username',
            password='your-rpc-password',
            callback_object_instance=self,
            callback_method_or_function_name='callback_method_irc'
        )

        if self.liverpc.get_error.code != 0:
            print(self.liverpc.get_error.message, self.liverpc.get_error.code)
            return

        self.liverpc.subscribe(['all'])

    def callback_method_irc(self, response):

        if hasattr(response, 'result'):
            if isinstance(response.result, bool) and response.result:
                print(self.liverpc.get_error)
                return

        level = response.result.level if hasattr(response.result, 'level') else ''
        subsystem = response.result.subsystem if hasattr(response.result, 'subsystem') else ''
        event_id = response.result.event_id if hasattr(response.result, 'event_id') else ''
        log_source = response.result.log_source if hasattr(response.result, 'log_source') else ''
        msg = response.result.msg if hasattr(response.result, 'msg') else ''

        build_msg = f"{log_source}: [{level}] {subsystem}.{event_id} - {msg}"
        print(build_msg)
        print(self.liverpc.get_error)


CallBack()

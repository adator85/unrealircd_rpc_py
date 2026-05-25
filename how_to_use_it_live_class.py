import asyncio
import time
import threading
from unrealircd_rpc_py.LiveConnectionFactory import LiveConnectionFactory
from unrealircd_rpc_py.objects.Definition import LiveRPCResult

###############
# CREDENTIALS #
###############

url = 'https://your.rpc.link:PORT/api'
username = 'Your-rpc-username'
password = 'your-rpc-password'
callback_method_name = 'callback_method_irc'

########################################
# How to connect using callback method #
########################################

class CallBack:

    def __init__(self):
        self.liverpc = LiveConnectionFactory().get('http')
        self.liverpc.setup({
            'url': url,
            'username': username,
            'password': password,
            'callback_object_instance' : self,
            'callback_method_or_function_name': callback_method_name
        })

    def thread_subscribe(self) -> None:

        response = asyncio.run(self.liverpc.subscribe())
        print("[JSONRPC SUBSCRIBE] Subscribe to the stream!")
        print(response)

    def thread_unsubscribe(self) -> None:

        response = asyncio.run(self.liverpc.unsubscribe())
        print("[JSONRPC UNSUBSCRIBE] Unsubscribe from the stream!")
        print(response)

    @staticmethod
    def callback_method_irc(response: LiveRPCResult) -> None:
        # Response model: https://www.unrealircd.org/docs/JSON-RPC:Log#log.subscribe
        # Possible responses: https://www.unrealircd.org/docs/List_of_all_log_messages

        # High level error
        if response.error.code != 0:
            print("ERROR:", response.error.code, response.error.message)
            return

        if isinstance(response.result, bool):
            if response.result:
                print(f"{response.method} has been activated")
            return

        level = response.result.level if hasattr(response.result, 'level') else ''
        subsystem = response.result.subsystem if hasattr(response.result, 'subsystem') else ''
        event_id = response.result.event_id if hasattr(response.result, 'event_id') else ''
        log_source = response.result.log_source if hasattr(response.result, 'log_source') else ''
        msg = response.result.msg if hasattr(response.result, 'msg') else ''

        build_msg = f"{log_source}: [{level}] {subsystem}.{event_id} - {msg}"
        print(build_msg)


live_stream = CallBack()
th_subscribe = threading.Thread(target=live_stream.thread_subscribe)
th_unsubscribe = threading.Thread(target=live_stream.thread_unsubscribe)

# Subscribe to the stream
th_subscribe.start()

# Do some stuff
time.sleep(2)

# If you want to disconnect from the stream
# run your unsubscribe thread
th_unsubscribe.start()

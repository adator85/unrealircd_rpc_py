import asyncio
import sys
import time
import threading
from types import SimpleNamespace
from unrealircd_rpc_py.Live import LiveWebsocket

##########################################
# How to connect using callback function #
##########################################

def callback_function_irc(response: SimpleNamespace) -> None:
    # Response model: https://www.unrealircd.org/docs/JSON-RPC:Log#log.subscribe
    # Possible responses: https://www.unrealircd.org/docs/List_of_all_log_messages

    # High level error
    if liverpc.get_error.code != 0:
        print("ERROR:", liverpc.get_error.code, liverpc.get_error.message)
        return

    # Because of the concurrent approach! there is also local errors
    if hasattr(response, 'error'):
        # Check if you are allowed to use log endpoint
        print(response.error.code, response.error.message)
        return

    if hasattr(response, 'result'):
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

# Init your live stream using websocket
liverpc = LiveWebsocket(
            url="https://your.rpc.link:PORT/api",
            username='Your-rpc-username',
            password='your-rpc-password',
            callback_object_instance=sys.modules[__name__],
            callback_method_or_function_name='callback_function_irc'
        )

def thread_subscribe() -> None:
    # This will run until the thread_unsubscribe is called!
    response = asyncio.run(liverpc.subscribe(["all"]))
    print(f"FINAL RESPONSE OF SUBSCRIBE: {response}")

def thread_unsubscribe() -> None:
    response = asyncio.run(liverpc.unsubscribe())
    print(f"FINAL RESPONSE OF UNSUBSCRIBE: {response}")


th_subscribe = threading.Thread(target=thread_subscribe, daemon=False)
th_unsubscribe = threading.Thread(target=thread_unsubscribe, daemon=False)

# Subscribe to the stream
th_subscribe.start()

# Do some stuff
time.sleep(2)

# If you want to disconnect from the stream
# run your new unsubscribe thread
th_unsubscribe.start()

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

    def thread_subscribe(self) -> None:

        response: dict[str, dict] = asyncio.run(self.liverpc.subscribe())
        print("[JSONRPC SUBSCRIBE] Subscribe to the stream!")
        print(response)

    def thread_unsubscribe(self) -> None:

        response: dict[str, dict] = asyncio.run(self.liverpc.unsubscribe())
        print("[JSONRPC UNSUBSCRIBE] Unsubscribe from the stream!")
        print(response)

    def callback_method_irc(self, response: SimpleNamespace) -> None:
        # Response model: https://www.unrealircd.org/docs/JSON-RPC:Log#log.subscribe
        # Possible responses: https://www.unrealircd.org/docs/List_of_all_log_messages

        # High level error
        if self.liverpc.get_error.code != 0:
            print("ERROR:", self.liverpc.get_error.code, self.liverpc.get_error.message)
            return

        # Because of the concurrent approach! there is also local errors
        if hasattr(response, 'error'):
            # Check if you are allowed to use log endpoint
            print(response.error.code, response.error.message)
            return

        if hasattr(response, 'result'):
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

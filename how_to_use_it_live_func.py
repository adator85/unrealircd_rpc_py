import asyncio
import sys
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
params = {
    'url': url,
    'username': username,
    'password': password,
    'callback_object_instance' : sys.modules[__name__],
    'callback_method_or_function_name': 'callback_function_irc'
}


##########################################
# How to connect using callback function #
##########################################

def callback_function_irc(response: LiveRPCResult) -> None:
    # Response model: https://www.unrealircd.org/docs/JSON-RPC:Log#log.subscribe
    # Possible responses: https://www.unrealircd.org/docs/List_of_all_log_messages

    # High level error
    if response.error.code != 0:
        # Check if you are allowed to use log endpoint
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

def thread_subscribe() -> None:
    # This thread will run until the thread_unsubscribe is called!
    response = asyncio.run(liverpc.subscribe(["all"]))
    print(f"FINAL RESPONSE OF SUBSCRIBE: {response}")

def thread_unsubscribe() -> None:
    response = asyncio.run(liverpc.unsubscribe())
    print(f"FINAL RESPONSE OF UNSUBSCRIBE: {response}")

# Init your live stream using websocket
liverpc = LiveConnectionFactory(10).get('http')
liverpc.setup(params)

th_subscribe = threading.Thread(target=thread_subscribe, daemon=True)
th_unsubscribe = threading.Thread(target=thread_unsubscribe, daemon=False)

# Subscribe to the stream
th_subscribe.start()

# Do some stuff
time.sleep(2)

# If you want to disconnect from the stream
# run your new unsubscribe thread
th_unsubscribe.start()

from datetime import datetime
import logging
import os
from re import match
from secrets import token_hex
from types import SimpleNamespace
from typing import Any, Optional, Union
import unrealircd_rpc_py.objects.Definition as Dfn
from unrealircd_rpc_py.exceptions.rpc_exceptions import (
    RpcInvalidUrlFormat,
    RpcUnixSocketFileNotFoundError
)


def check_unix_socket_file(path_to_socket_file: str) -> bool:
    """Check provided full path to socket file if it exist

    Args:
        path_to_socket_file (str): Full path to unix socket file

    Returns:
        bool: True if path is correct else False
    """
    if path_to_socket_file is None:
        return False

    if not os.path.exists(path_to_socket_file):
        return False

    return True


def check_url(url: str) -> Optional[tuple[str, str, int]]:
    """Check provided url if it follow the format

    Args:
        url (str): Url to jsonrpc https://your.rpcjson.link:port/api

    Returns:
        tuple: (host, endpoint, port) or None
    """
    if url is None or not url:
        return None

    pattern = r'https?://([a-zA-Z0-9\.-]+):(\d+)/(.+)'

    match_url = match(pattern, url)

    if match_url is not None:
        host = match_url.group(1)
        endpoint = match_url.group(3)
        port = match_url.group(2)
        return host, endpoint, port
    else:
        return None


def construct_rpc_response(response: dict) -> Dfn.RPCResult:
    """Construct the rpc result

    Args:
        response (dict): The response you want to construct

    Returns:
        RPCResult: The RPC Result
        ```python
            RPCResult(jsonrpc='2.0',
                 method='method.name',
                 error=RPCErrorModel(code=0, message=None),
                 result={},
                 id=1760041102
                 )
        ```
    """
    error_dict = response.pop('error', {})
    error_model = Dfn.RPCErrorModel()
    if error_dict:
        error_model = Dfn.RPCErrorModel(**error_dict)

    return Dfn.RPCResult(**response, error=error_model)


def get_timestamp() -> str:
    return datetime.now().__str__()


def decompose_url(url: str) -> tuple[str, str, int]:
    """Check provided url if it follow the format
    and decompose it to host, endpoint and port

    >>> # If error it raises RpcInvalidUrlFormat exception
    Args:
        url (str): Url to jsonrpc https://your.rpcjson.link:port/api

    Returns:
        tuple: Host, Endpoint, Port
    """
    if url is None or url == '':
        raise RpcInvalidUrlFormat("The url provided is empty!")

    pattern = r'https?://([a-zA-Z0-9\.-]+):(\d+)/(.+)'

    match_url = match(pattern, url)

    if match_url is not None:
        port = match_url.group(2)
        host = match_url.group(1)
        endpoint = match_url.group(3)
        return host, endpoint, int(port)
    else:
        raise RpcInvalidUrlFormat(
            "You must provide the url in this format: "
            "https://your.rpcjson.link:port/api"
        )


def dict_to_namespace(dictionary: Any) -> Union[SimpleNamespace, Any]:
    """Try to convert a dictionary to a SimpleNamespace object

    :param dictionary:
    :return: SimpleNamespace object or the object
    if it was impossible to convert
    """
    if isinstance(dictionary, dict):
        return SimpleNamespace(
            **{key: dict_to_namespace(value)
               for key, value in dictionary.items()}
        )
    else:
        return dictionary


def verify_unix_socket_file(path_to_socket_file: str) -> bool:
    """Check provided full path to socket file if it exist

    Args:
        path_to_socket_file (str): Full path to unix socket file

    Returns:
        bool: True if path is correct else False
    """
    if path_to_socket_file is None or not os.path.exists(path_to_socket_file):
        raise RpcUnixSocketFileNotFoundError(
            "The socket file is not available, "
            "please check the full path of your socket file"
        )

    return True


def convert_to_jsonrpc_result(result: Union[dict, Any]) -> Dfn.LiveRPCResult:

    if not isinstance(result, dict):
        raise TypeError("Invalid jsonrpc response!")

    return Dfn.LiveRPCResult(**result)


def remove_logger(logger_name: str) -> None:

    # Get the logger name
    logger = logging.getLogger(logger_name)

    # Delete handlers from the gestionary and close them
    for handler in logger.handlers[:]:  # Use a copy of the list
        # print(handler)
        logger.removeHandler(handler)
        handler.close()

    # Remove the logger from the dictionary
    logging.Logger.manager.loggerDict.pop(logger_name, None)

    return None


def start_log_system(name: str, debug_level: int = 20) -> logging.Logger:
    """Init log system
    """
    logger_name = name
    remove_logger(logger_name)

    # Init logs object
    logger: logging.Logger = logging.getLogger(logger_name)
    logger.setLevel(debug_level)

    # Add Handlers
    stdout_hanlder = logging.StreamHandler()
    stdout_hanlder.setLevel(debug_level)

    # Define log format
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s '
        '(%(filename)s::%(funcName)s::%(lineno)d)',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Apply log format
    stdout_hanlder.setFormatter(formatter)

    # Add handler to logs
    logger.addHandler(stdout_hanlder)

    return logger


def is_version_ircd_ok(
        current_server_version: Optional[tuple] = None,
        minimum_version: Optional[tuple] = None
) -> bool:
    """Check if the version is allowed or not

    Args:
        current_server_version (Optional[tuple]): _description_
        minimum_version (Optional[tuple]): _description_
    """

    if (isinstance(current_server_version, tuple)
            and isinstance(minimum_version, tuple)):
        if current_server_version >= minimum_version:
            return True
        else:
            return False
    else:
        return True


def generate_ids(nbytes: int = 16) -> str:
    """Generates a random hexadecimal token for IDs.
        Args:
            nbytes (int, optional): The number of bytes to use when
                                    generating the token. Defaults to 16.
        Returns:
            Union[str, None]: A string containing the hexadecimal
                              representation of the token, or None
                              if an error occurred.
    """
    return token_hex(nbytes)

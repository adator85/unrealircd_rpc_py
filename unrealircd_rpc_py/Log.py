from types import SimpleNamespace
from typing import Union, Literal
from time import time
from unrealircd_rpc_py.Connection import Connection
# import Definition

class Log:

    # DB_LOG_CONNECT: list[Definition.LogConnect]

    def __init__(self, Connection: Connection) -> None:

        # Store the original response
        self.response_raw: str
        """Original response used to see available keys."""

        self.response_np: SimpleNamespace
        """Parsed JSON response providing access to all keys as attributes."""

        # Get the Connection instance
        self.Connection = Connection
        self.Logs = Connection.Logs
        self.Error = Connection.Error

    def list_(self, sources: list = None) -> Union[SimpleNamespace, None]:
        """Fetch past log entries (since boot).

        Returns:
            list[ModelNameBan]: List of ModelNameBan, None if nothing or Error see the property
        """
        try:
            response = self.Connection.query(
                method='log.list', 
                param={"sources": sources}
                )

            self.response_raw = response
            self.response_np = self.Connection.json_response_np

            if response is None:
                error = {"error": {"code": -1, "message": "Empty response"}}
                self.Connection.set_error(error)
                return None

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.set_error(response)
                return None

            return self.response_np

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
        except Exception as err:
            self.Logs.error(f'General error: {err}')

    def send(self, msg: str, level: Literal['debug','info','warn','error','fatal'], subsystem: str, event_id: str, timestamp: float = time()) -> bool:
        """ Send a log message / server notice.

        Requires UnrealIRCd 6.1.8 or later

        Args:
            msg (str): The message you want to send to the server
            level (Literal[&#39;debug&#39;,&#39;info&#39;,&#39;warn&#39;,&#39;error&#39;,&#39;fatal&#39;]): You can pick the level in the list
            subsystem (str): You can put anything you want as a subsystem
            event_id (str): You can put anything you want as a event_id
            timestamp (float, optional): The current timestamp. Defaults to time().

        Returns:
            bool: True if is okey, else if there is an error
        """
        # waiting for the documentation.
        try:
            response = self.Connection.query(
                    method='log.send',
                    param={"msg": msg, "level": level, "subsystem": subsystem, "event_id": event_id, "timestamp": timestamp}
                    )

            self.response_raw = response
            self.response_np = self.Connection.json_response_np

            if 'error' in response:
                self.Logs.error(response["error"])
                self.Connection.set_error(response)
                return False

            self.Logs.debug(response)

            return True

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return False
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return False
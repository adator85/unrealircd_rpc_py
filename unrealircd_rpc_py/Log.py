from types import SimpleNamespace
from typing import Union
from dataclasses import dataclass
from unrealircd_rpc_py.Connection import Connection

class Log:

    @dataclass
    class ModelLog:
        type: str
        type_string: str
        set_by: str
        set_at: str
        expire_at: str
        set_at_string: str
        expire_at_string: str
        duration_string: str
        set_at_delta: int
        set_in_config: bool
        name: str
        reason: str

    DB_NAME_BANS: list[ModelLog] = []


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

    def list_(self, sources: list = None) -> Union[SimpleNamespace, None, bool]:
        """Fetch past log entries (since boot).

        Returns:
            Union[list[ModelNameBan], None, bool]: List of ModelNameBan, None if nothing or False if error
        """
        try:
            response = self.Connection.query(
                method='log.list', 
                param={"sources": sources}
                )

            self.response_raw = response
            self.response_np = self.Connection.json_response_np

            if response is None:
                return False

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.set_error(response)
                return False

            return self.response_np

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
        except Exception as err:
            self.Logs.error(f'General error: {err}')

    def subscribe(self, sources: list) -> bool:
        """Subscribe to one or more log sources. Any previous subscriptions are overwritten (lost).

        Args:
            sources (list): an array of log sources. See log block sources. 
            For example ["!debug","all"] would give you all log messages except for debug messages. And ["connect"] would give only client connects/disconnects.

        Returns:
            bool: True if success
        """
        try:
            response = self.Connection.query(
                method='log.subscribe', 
                param={"sources": sources}
                )

            self.response_raw = response
            self.response_np = self.Connection.json_response_np

            if response is None:
                return False

            if 'error' in response:
                self.Connection.set_error(response)
                return False

            if 'result' in response:
                if response['result']:
                    self.Logs.debug(response)
                    return True
                else:
                    self.Logs.debug(response)
                    return False

            return True

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
        #except Exception as err:
        #    self.Logs.error(f'General error: {err}')

    def unsubscribe(self) -> bool:
        """Unsubscribe from all log events.
        After this UnrealIRCd will stop streaming log events to you.

        Returns:
            bool: Always returns true
        """
        try:
            response = self.Connection.query(
                method='log.unsubscribe'
                )

            self.response_raw = response
            self.response_np = self.Connection.json_response_np

            if response is None:
                return False

            if 'error' in response:
                self.Connection.set_error(response)
                return False

            if 'result' in response:
                if response['result']:
                    self.Logs.debug(response)
                    return True
                else:
                    self.Logs.debug(response)
                    return False

            return True

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
        except Exception as err:
            self.Logs.error(f'General error: {err}')

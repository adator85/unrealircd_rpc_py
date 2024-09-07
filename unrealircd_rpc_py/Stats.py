from types import SimpleNamespace
from typing import Union
from dataclasses import dataclass
from unrealircd_rpc_py.Connection import Connection

class Stats:

    @dataclass
    class ModelStats:
        server_total: int
        server_ulined: int
        user_total: int
        user_ulined: int
        user_oper: int
        user_record: int
        user_countries: list[dict[str, any]]
        channel_total: int
        server_ban_total: int
        server_ban_server_ban: int
        server_ban_spamfilter: int
        server_ban_name_ban: int
        server_ban_server_ban_exception: int

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

    def get(self, _object_detail_level:int = 1) -> Union[ModelStats, None]:
        """Get some quick basic statistics.

        Args:
            _object_detail_level (int, optional): set the detail of the response object. The user.countries will be included from level 1+. The default object_detail_level is 1. Defaults to 1.

        Returns:
            Union[list[ModelStats], None, bool]: _description_
        """
        try:
            response = self.Connection.query('stats.get', param={'object_detail_level': _object_detail_level})

            self.response_raw = response
            self.response_np = self.Connection.json_response_np

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.set_error(response)
                return False

            stats = response['result']

            statsModel = self.ModelStats(
                    server_total=stats['server']['total'] if 'server' in stats and 'total' in stats['server'] else 0,
                    server_ulined=stats['server']['ulined'] if 'server' in stats and 'ulined' in stats['server'] else 0,

                    user_total=stats['user']['total'] if 'user' in stats and 'total' in stats['user'] else 0,
                    user_ulined=stats['user']['ulined'] if 'user' in stats and 'total' in stats['user'] else 0,
                    user_oper=stats['user']['oper'] if 'user' in stats and 'oper' in stats['user'] else 0,
                    user_record=stats['user']['record'] if 'user' in stats and 'record' in stats['user'] else 0,
                    user_countries=stats['user']['countries'] if 'user' in stats and 'countries' in stats['user'] else [],
                    
                    channel_total=stats['channel']['total'] if 'channel' in stats and 'total' in stats['channel'] else 0,

                    server_ban_total=stats['server_ban']['total'] if 'server_ban' in stats and 'total' in stats['server_ban'] else 0,
                    server_ban_server_ban=stats['server_ban']['server_ban'] if 'server_ban' in stats and 'server_ban' in stats['server_ban'] else 0,
                    server_ban_spamfilter=stats['server_ban']['spamfilter'] if 'server_ban' in stats and 'spamfilter' in stats['server_ban'] else 0,
                    server_ban_name_ban=stats['server_ban']['name_ban'] if 'server_ban' in stats and 'name_ban' in stats['server_ban'] else 0,
                    server_ban_server_ban_exception=stats['server_ban']['server_ban_exception'] if 'server_ban' in stats and 'server_ban_exception' in stats['server_ban'] else 0
                )

            return statsModel

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
        except Exception as err:
            self.Logs.error(f'General error: {err}')



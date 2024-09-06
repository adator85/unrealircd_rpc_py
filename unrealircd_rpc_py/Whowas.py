from typing import Union
from dataclasses import dataclass
from unrealircd_rpc_py.Connection import Connection

class Whowas:

    @dataclass
    class ModelWhowas:
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

        # Record the original response
        self.original_response: str = ''

        # Get the Connection instance
        self.Connection = Connection
        self.Logs = Connection.Logs
        self.Error = Connection.Error

    def get(self, _nick: str = '', _ip: str = '', _object_detail_level:int = 2) -> Union[ModelWhowas, None, bool]:
        """Get WHOWAS history of a user. 6.1.0+

        Args:
            _nick (str, optional): The nick name to search for. Defaults to ''.
            _ip (str, optional): The IP address to search for. Defaults to ''.
            _object_detail_level (int, optional): set the detail of the response object, this is similar to the Detail level column in Structure of a client object. In this RPC call it defaults to 2 if this parameter is not specified. Defaults to 2.

        Returns:
            [ModelWhowas, None, bool]: If success it return the object ModelWhowas | None if nothing | False if error
        """
        try:
            response = self.Connection.query('whowas.get', param={'nick': _nick, 'ip': _ip, 'object_detail_level': _object_detail_level})
            self.original_response = response

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.set_error(response)
                return False

            # stats = response['result']

            # statsModel = self.ModelStats(
            #         server_total=stats['server']['total'] if 'server' in stats and 'total' in stats['server'] else 0,
            #         server_ulined=stats['server']['ulined'] if 'server' in stats and 'ulined' in stats['server'] else 0,

            #         user_total=stats['user']['total'] if 'user' in stats and 'total' in stats['user'] else 0,
            #         user_ulined=stats['user']['ulined'] if 'user' in stats and 'total' in stats['user'] else 0,
            #         user_oper=stats['user']['oper'] if 'user' in stats and 'oper' in stats['user'] else 0,
            #         user_record=stats['user']['record'] if 'user' in stats and 'record' in stats['user'] else 0,
            #         user_countries=stats['user']['countries'] if 'user' in stats and 'countries' in stats['user'] else [],
                    
            #         channel_total=stats['channel']['total'] if 'channel' in stats and 'total' in stats['channel'] else 0,

            #         server_ban_total=stats['server_ban']['total'] if 'server_ban' in stats and 'total' in stats['server_ban'] else 0,
            #         server_ban_server_ban=stats['server_ban']['server_ban'] if 'server_ban' in stats and 'server_ban' in stats['server_ban'] else 0,
            #         server_ban_spamfilter=stats['server_ban']['spamfilter'] if 'server_ban' in stats and 'spamfilter' in stats['server_ban'] else 0,
            #         server_ban_name_ban=stats['server_ban']['name_ban'] if 'server_ban' in stats and 'name_ban' in stats['server_ban'] else 0,
            #         server_ban_server_ban_exception=stats['server_ban']['server_ban_exception'] if 'server_ban' in stats and 'server_ban_exception' in stats['server_ban'] else 0
            #     )

            return None

        except KeyError as ke:
            self.Logs.error(str(ke))



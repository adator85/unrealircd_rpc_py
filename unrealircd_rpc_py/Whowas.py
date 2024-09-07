from typing import Union
from dataclasses import dataclass
from unrealircd_rpc_py.Connection import Connection

class Whowas:

    @dataclass
    class ModelWhowas:
        name: str
        event: str
        logon_time: str
        logoff_time: str
        hostname: str
        ip: str
        details: str
        connected_since: str
        user_username: str
        user_realname: str
        user_vhost: str
        user_servername: str
        geoip_country_code: str
        geoip_asn: str
        geoip_asname: str

    DB_WHOWAS: list[ModelWhowas] = []

    def __init__(self, Connection: Connection) -> None:

        # Record the original response
        self.original_response: str = ''

        # Get the Connection instance
        self.Connection = Connection
        self.Logs = Connection.Logs
        self.Error = Connection.Error

    def get(self, _nick: str = None, _ip: str = None, _object_detail_level:int = 2) -> Union[list[ModelWhowas], None, bool]:
        """Get WHOWAS history of a user. 6.1.0+

        Args:
            _nick (str, optional): The nick name to search for. Defaults to None.
            _ip (str, optional): The IP address to search for. Defaults to None.
            _object_detail_level (int, optional): set the detail of the response object, this is similar to the Detail level column in Structure of a client object. In this RPC call it defaults to 2 if this parameter is not specified. Defaults to 2.

        Returns:
            [ModelWhowas, None, bool]: If success it return the object ModelWhowas | None if nothing | False if error
        """
        try:
            response = self.Connection.query('whowas.get', param={'nick': _nick, 'ip': _ip, 'object_detail_level': _object_detail_level})
            self.original_response = response

            if response is None:
                return False

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.set_error(response)
                return False

            whowass = response['result']['list']

            for whowas in whowass:
                self.DB_WHOWAS.append(
                    self.ModelWhowas(
                        name=whowas['name'] if 'name' in whowas else None,
                        event=whowas['event'] if 'event' in whowas else None,
                        logon_time=whowas['logon_time'] if 'logon_time' in whowas else None,
                        logoff_time=whowas['logoff_time'] if 'logoff_time' in whowas else None,
                        hostname=whowas['hostname'] if 'hostname' in whowas else None,
                        ip=whowas['ip'] if 'ip' in whowas else None,
                        details=whowas['details'] if 'details' in whowas else None,
                        connected_since=whowas['connected_since'] if 'connected_since' in whowas else None,
                        user_username=whowas['user'] if 'user' in whowas and 'username' in whowas['user'] else None,
                        user_realname=whowas['user'] if 'user' in whowas and 'realname' in whowas['user'] else None,
                        user_vhost=whowas['user'] if 'user' in whowas and 'vhost' in whowas['user'] else None,
                        user_servername=whowas['user'] if 'user' in whowas and 'servername' in whowas['user'] else None,
                        geoip_country_code=whowas['geoip'] if 'geoip' in whowas and 'username' in whowas['geoip'] else None,
                        geoip_asn=whowas['geoip'] if 'geoip' in whowas and 'asn' in whowas['geoip'] else None,
                        geoip_asname=whowas['geoip'] if 'geoip' in whowas and 'asname' in whowas['geoip'] else None
                        )
                    )

            return self.DB_WHOWAS

        except KeyError as ke:
            self.Logs.error(str(ke))



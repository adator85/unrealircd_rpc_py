from types import SimpleNamespace
from typing import Union
from dataclasses import dataclass
from unrealircd_rpc_py.Connection import Connection

class User:

    @dataclass
    class ModelUser:
        name: str
        id: str
        hostname: str
        ip: str
        details: str
        server_port: int
        client_port: int
        connected_since: str
        idle_since: str
        username: str
        realname: str
        vhost: str
        cloakedhost: str
        servername: str
        reputation: int
        security_groups: list
        modes: str
        channels: list[dict[str, str]]
        cipher: str
        certfp: str
        country_code: str
        asn: str
        asname: str

    DB_USER: list[ModelUser] = []

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

    def list_(self) -> Union[list[ModelUser], None]:
        """List users.

        Returns:
            ModelUser (list[ModelUser]): List with an object contains all Users information
        """
        try:
            response = self.Connection.query('user.list', param={'object_detail_level': 4})

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

            users = response['result']['list']

            for user in users:
                self.DB_USER.append(
                        self.ModelUser(
                            name=user['name'] if 'name' in user else None,
                            id=user['id'] if 'id' in user else None,
                            hostname=user['hostname'] if 'hostname' in user else None,
                            ip=user['ip'] if 'ip' in user else None,
                            details=user['details'] if 'details' in user else None,
                            server_port=user['server_port'] if 'server_port' in user else 0,
                            client_port=user['client_port'] if 'client_port' in user else 0,
                            connected_since=user['connected_since'] if 'connected_since' in user else None,
                            idle_since=user['idle_since'] if 'idle_since' in user else None,
                            username=user['user']['username'] if 'user' in user and 'username' in user['user'] else None,
                            realname=user['user']['realname'] if 'user' in user and 'realname' in user['user'] else None,
                            vhost=user['user']['vhost'] if 'user' in user and 'vhost' in user['user'] else None,
                            cloakedhost=user['user']['cloakedhost'] if 'user' in user and 'cloakedhost' in user['user'] else None,
                            servername=user['user']['servername'] if 'user' in user and 'servername' in user['user'] else None,
                            reputation=user['user']['reputation'] if 'user' in user and 'reputation' in user['user'] else 0,
                            security_groups=user['user']['security-groups'] if 'user' in user and 'security-groups' in user['user'] else [],
                            modes=user['user']['modes'] if 'user' in user and 'modes' in user['user'] else None,
                            channels=user['user']['channels'] if 'user' in user and 'channels' in user['user'] else [{}],
                            cipher=user['tls']['cipher'] if 'tls' in user and 'cipher' in user['tls'] else None,
                            certfp=user['tls']['certfp'] if 'tls' in user and 'certfp' in user['tls'] else None,
                            country_code=user['geoip']['country_code'] if 'geoip' in user and 'country_code' in user['geoip'] else None,
                            asn=user['geoip']['asn'] if 'geoip' in user and 'asn' in user['geoip'] else None,
                            asname=user['geoip']['asname'] if 'geoip' in user and 'asname' in user['geoip'] else None
                        )
                )

            return self.DB_USER

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
        except Exception as err:
            self.Logs.error(f'General error: {err}')

    def get(self, nickoruid: str) -> Union[ModelUser, None]:
        """Get user information

        Args:
            nickoruid (str): The nickname or uid of the user

        Returns:
            ModelUser (ModelUser): If success it return the object ModelUser

            None (None): if no value found, Probably you can see Error property
        """
        try:

            response = self.Connection.query('user.get', {'nick': nickoruid})

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

            user = response['result']['client']

            userObject = self.ModelUser(
                    name=user['name'] if 'name' in user else None,
                    id=user['id'] if 'id' in user else None,
                    hostname=user['hostname'] if 'hostname' in user else None,
                    ip=user['ip'] if 'ip' in user else None,
                    details=user['details'] if 'details' in user else None,
                    server_port=user['server_port'] if 'server_port' in user else 0,
                    client_port=user['client_port'] if 'client_port' in user else 0,
                    connected_since=user['connected_since'] if 'connected_since' in user else None,
                    idle_since=user['idle_since'] if 'idle_since' in user  else None,
                    username=user['user']['username'] if 'user' in user and 'username' in user['user'] else None,
                    realname=user['user']['realname'] if 'user' in user and 'realname' in user['user'] else None,
                    vhost=user['user']['vhost'] if 'user' in user and 'vhost' in user['user'] else None,
                    cloakedhost=user['user']['cloakedhost'] if 'user' in user and 'cloakedhost' in user['user'] else None,
                    servername=user['user']['servername'] if 'user' in user and 'servername' in user['user'] else None,
                    reputation=user['user']['reputation'] if 'user' in user and 'reputation' in user['user'] else 0,
                    security_groups=user['user']['security-groups'] if 'user' in user and 'security-groups' in user['user'] else [],
                    modes=user['user']['modes'] if 'user' in user and 'modes' in user['user'] else None,
                    channels=user['user']['channels'] if 'user' in user and 'channels' in user['user'] else [],
                    cipher=user['tls']['cipher'] if 'tls' in user and 'cipher' in user['tls'] else None,
                    certfp=user['tls']['certfp'] if 'tls' in user and 'certfp' in user['tls'] else None,
                    country_code=user['geoip']['country_code'] if 'geoip' in user and 'country_code' in user['geoip'] else None,
                    asn=user['geoip']['asn'] if 'geoip' in user and 'asn' in user['geoip'] else None,
                    asname=user['geoip']['asname'] if 'geoip' in user and 'asname' in user['geoip'] else None
                )

            return userObject

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return None
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return None

    def set_nick(self, nickoruid: str, newnick: str, _force: bool = False) -> bool:
        """Sets the nick name of a user (changes the nick).
        force: if set to true then q-lines (banned nick) checks will be bypassed. And also, 
        if the new nick name already exists, the other existing user is killed and we will take that new nick.

        Args:
            nick (str): the nick name or the UID
            newnick (str): the new nick name
            force (bool, optional): q-lines (banned nick) checks will be bypassed. Defaults to False.

        Returns:
            bool: True if success else error will be stored in ErrorModel
        """
        try:
            response = self.Connection.query('user.set_nick', {'nick': nickoruid, 'newnick': newnick, 'force': _force})

            self.response_raw = response
            self.response_np = self.Connection.json_response_np

            if response is None:
                return False

            if 'error' in response:
                self.Connection.set_error(response)
                return False

            return True

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
        except Exception as err:
            self.Logs.error(f'General error: {err}')

    def set_username(self, nickoruid: str, username:str) -> bool:
        """Set the username / ident of a user.

        Args:
            nickoruid (str): the nick name or the UID
            username (str): the new user name / ident

        Returns:
            bool: True if success else error will be stored in ErrorModel
        """
        try:
            response = self.Connection.query('user.set_username', {'nick': nickoruid, 'username': username})

            self.response_raw = response
            self.response_np = self.Connection.json_response_np

            if response is None:
                return False

            if 'error' in response:
                self.Connection.set_error(response)
                return False

            return True

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
        except Exception as err:
            self.Logs.error(f'General error: {err}')

    def set_realname(self, nickoruid: str, realname:str) -> bool:
        """Set the realname / gecos of a user.

        Args:
            nickoruid (str): the nick name or the UID
            realname (str):  the new realname / gecos of a user.

        Returns:
            bool: True if success else error will be stored in ErrorModel
        """
        try:
            response = self.Connection.query('user.set_realname', {'nick': nickoruid, 'realname': realname})

            self.response_raw = response
            self.response_np = self.Connection.json_response_np

            if response is None:
                return False

            if 'error' in response:
                self.Connection.set_error(response)
                return False

            return True

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
        except Exception as err:
            self.Logs.error(f'General error: {err}')

    def set_vhost(self, nickoruid: str, vhost:str) -> bool:
        """Set a virtual host (vhost) on the user.

        Args:
            nickoruid (str): the nick name or the UID
            vhost (str): the new virtual host.

        Returns:
            bool: True if success else error will be stored in ErrorModel
        """
        try:
            response = self.Connection.query('user.set_vhost', {'nick': nickoruid, 'vhost': vhost})

            self.response_raw = response
            self.response_np = self.Connection.json_response_np

            if response is None:
                return False

            if 'error' in response:
                self.Connection.set_error(response)
                return False

            return True

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
        except Exception as err:
            self.Logs.error(f'General error: {err}')

    def set_mode(self, nickoruid: str, modes:str) -> bool:
        """Change the modes of a user.

        Args:
            nickoruid (str): the nick name or the UID
            modes (str): the mode string, eg -i+w

        Returns:
            bool: True if success else error will be stored in ErrorModel
        """
        try:
            response = self.Connection.query('user.set_mode', {'nick': nickoruid, 'modes': modes})

            self.response_raw = response
            self.response_np = self.Connection.json_response_np

            if response is None:
                return False

            if 'error' in response:
                self.Connection.set_error(response)
                return False

            return True

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
        except Exception as err:
            self.Logs.error(f'General error: {err}')

    def set_snomask(self, nickoruid: str, snomask:str) -> bool:
        """Change the snomask of a user.

        Args:
            nickoruid (str): the nick name or the UID
            snomask (str): the snomask string, eg -j+R

        Returns:
            bool: True if success else error will be stored in ErrorModel
        """
        try:
            response = self.Connection.query('user.set_snomask', {'nick': nickoruid, 'snomask': snomask})

            self.response_raw = response
            self.response_np = self.Connection.json_response_np

            if response is None:
                return False

            if 'error' in response:
                self.Connection.set_error(response)
                return False

            return True

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
        except Exception as err:
            self.Logs.error(f'General error: {err}')

    def set_oper(self, nickoruid: str, oper_account:str, oper_class: str, _class: str = '', _modes: str = '', _snomask: str = '', _vhost: str = '') -> bool:
        """Make user an IRC operator.

        Args:
            nickoruid (str): the nick name or the UID
            oper_account (str):  the oper account, to be shown in WHOIS to fellow ircops and in logs.
            oper_class (str):  the operclass. Usually one of the default operclasses like netadmin-with-override
            _class (str, optional): the class to put the user in. If this option is not specified then opers is assumed, since this class exists in most unrealircd.conf's. You can specify "" (empty) if you don't want to put the user in a class. Defaults to ''.
            _modes (str, optional): user modes to set on oper. For example: +xws. If this option is not specified then set::modes-on-oper is used. You can specify "" (empty) if you don't want to set any additional modes on the user. Defaults to ''.
            _snomask (str, optional): snomask to set on oper. For example: +bBcdfkqsSoO. If this option is not specified then set::snomask-on-oper is used. You can specify "" (empty) if you don't want to set any snomasks on the user. Defaults to ''.
            _vhost (str, optional): virtual host to set on oper. Defaults to ''.

        Returns:
            bool: True if success else error will be stored in ErrorModel
        """
        try:
            response = self.Connection.query('user.set_oper', {'nick': nickoruid, 'oper_account': oper_account, 'oper_class': oper_class, 'class': _class, 'modes': _modes, 'snomask': _snomask, 'vhost': _vhost})

            self.response_raw = response
            self.response_np = self.Connection.json_response_np

            if response is None:
                return False

            if 'error' in response:
                self.Connection.set_error(response)
                return False

            return True

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
        except Exception as err:
            self.Logs.error(f'General error: {err}')

    def join(self, nickoruid: str, channel:str, _key: str = '', _force: bool = False) -> bool:
        """Join a user to a channel.

        Note: If force is set to true then the user will walk through bans, modes and other restrictions 
        (similar to SAJOIN on IRC). If force is not set, or set to false, then it will be a regular JOIN attempt that may fail. 
        If it fails then the user will see an error message on their screen, such as for example Cannot join channel (+k).

        Args:
            nickoruid (str): the nick name or the UID
            channel (str): the channel(s) to join (e.g. #channel or #channel1,#channel2)
            _key (str, optional): the key of the channel(s) (only for channels with +k needed, again separate by colon for multiple channels). Defaults to ''.
            _force (bool, optional): whether to bypass join restrictions or not. Defaults to False.

        Returns:
            bool: True if success else error will be stored in ErrorModel
        """
        try:
            response = self.Connection.query('user.join', {'nick': nickoruid, 'channel': channel, 'key': _key, 'force': _force})

            self.response_raw = response
            self.response_np = self.Connection.json_response_np

            if response is None:
                return False

            if 'error' in response:
                self.Connection.set_error(response)
                return False

            return True

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
        except Exception as err:
            self.Logs.error(f'General error: {err}')

    def part(self, nickoruid: str, channel:str, _force: bool = False) -> bool:
        """Part a user from a channel.

        Note: If force is set to true then the user will see a notice that they were forcefully PARTed from the channel(s). 
        If force is not set, or set to false, then there will be no such notice.

        Args:
            nickoruid (str): the nick name or the UID
            channel (str): the channel(s) to join (e.g. #channel or #channel1,#channel2)
            _force (bool, optional): whether to bypass join restrictions or not. Defaults to False.

        Returns:
            bool: True if success else error will be stored in ErrorModel
        """
        try:
            response = self.Connection.query('user.part', {'nick': nickoruid, 'channel': channel, 'force': _force})

            self.response_raw = response
            self.response_np = self.Connection.json_response_np

            if response is None:
                return False

            if 'error' in response:
                self.Connection.set_error(response)
                return False

            return True

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
        except Exception as err:
            self.Logs.error(f'General error: {err}')

    def kill(self, nickoruid: str, reason:str) -> bool:
        """Kill a user, showing that the user was forcefully removed.

        Note: There is also user.quit. The difference is that user.kill will show that the user is forcefully killed, while user.quit pretend the user quit normally. 
        This slight difference may invoke certain client behavior. For example, some clients don't immediately reconnect for a KILL but do so on a QUIT.

        Args:
            nickoruid (str): the nick name or the UID
            reason (str): reason for the kill

        Returns:
            bool: True if success else error will be stored in ErrorModel
        """
        try:
            response = self.Connection.query('user.kill', {'nick': nickoruid, 'reason': reason})

            self.response_raw = response
            self.response_np = self.Connection.json_response_np

            if response is None:
                return False

            if 'error' in response:
                self.Connection.set_error(response)
                return False

            return True

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
        except Exception as err:
            self.Logs.error(f'General error: {err}')

    def quit(self, nickoruid: str, reason:str) -> bool:
        """Quit a user, pretending it was a normal QUIT.

        Note: There is also user.kill. The difference is that user.kill will show that the user is forcefully killed, 
        while user.quit pretend the user quit normally. This slight difference may invoke certain client behavior. 
        For example, some clients don't immediately reconnect for a KILL but do so on a QUIT.

        Args:
            nickoruid (str): the nick name or the UID
            reason (str): reason for the kill

        Returns:
            bool: True if success else error will be stored in ErrorModel
        """
        try:
            response = self.Connection.query('user.quit', {'nick': nickoruid, 'reason': reason})

            self.response_raw = response
            self.response_np = self.Connection.json_response_np

            if response is None:
                return False

            if 'error' in response:
                self.Connection.set_error(response)
                return False

            return True

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
        except Exception as err:
            self.Logs.error(f'General error: {err}')

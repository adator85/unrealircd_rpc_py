from typing import TYPE_CHECKING, Literal
import unrealircd_rpc_py.objects.Definition as Dfn
from unrealircd_rpc_py.utils import utils

if TYPE_CHECKING:
    from unrealircd_rpc_py.connections.sync.IConnection import IConnection


class User:

    DB_USER: list[Dfn.Client] = []

    def __init__(self, connection: 'IConnection') -> None:

        # Get the Connection instance
        self.Connection = connection
        self.Logs = connection.Logs

    def list_(
            self, object_detail_level: Literal[0, 1, 2, 4] = 2
    ) -> list[Dfn.Client]:
        """List users

        Args:
            object_detail_level (int, optional):
                set the detail of the response object,
                see the Detail level column in Structure
                of a client object. Defaults to 2.

        Returns:
            Client ([Dfn.Client]): List of Client Object
        """
        try:
            self.DB_USER = []
            response: dict[str, dict] = self.Connection.query(
                'user.list',
                param={'object_detail_level': object_detail_level})
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                self.DB_USER.append(
                    Dfn.Client(error=response_model.error)
                )
                return self.DB_USER

            users: list[dict] = response_model.result.get('list', [])

            for user in users:
                user_for_client = user.copy()
                user_for_user: dict = user.get('user', {}).copy()

                for key in ['geoip', 'tls', 'user']:
                    user_for_client.pop(key, None)

                for key in ['channels', 'security-groups']:
                    user_for_user.pop(key, None)

                user_model = Dfn.User(
                    **user_for_user,
                    security_groups=user.get('user', {}).get(
                        'security-groups', []),
                    channels=[Dfn.UserChannel(**chans)
                              for chans in user.get('user', {})
                              .get('channels',
                                   [Dfn.UserChannel().to_dict()]
                                   )]
                )

                self.DB_USER.append(
                        Dfn.Client(
                            **user_for_client,
                            geoip=Dfn.Geoip(
                                **user.get('geoip',
                                           Dfn.Geoip().to_dict())),
                            tls=Dfn.Tls(**user.get('tls',
                                                   Dfn.Tls().to_dict())),
                            user=user_model
                        )
                )

            return self.DB_USER

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return []
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return []

    def get(self, nickoruid: str) -> Dfn.Client:
        """Get user information

        Args:
            nickoruid (str): The nickname or uid of the user

        Returns:
            Client (Client): The object Client
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                'user.get',
                {'nick': nickoruid})
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                return Dfn.Client(error=response_model.error)

            user: dict[str, dict] = response_model.result.get('client', {})

            user_for_client = user.copy()
            user_for_user: dict = user.get('user', {}).copy()

            for key in ['geoip', 'tls', 'user']:
                user_for_client.pop(key, None)

            for key in ['channels', 'security-groups']:
                user_for_user.pop(key, None)

            user_model = Dfn.User(
                **user_for_user,
                security_groups=user.get('user', {}).get(
                    'security-groups', []),
                channels=[Dfn.UserChannel(**chans)
                          for chans in
                          user.get('user', {}).get('channels', [])]
            )

            user_obj = Dfn.Client(
                        **user_for_client,
                        geoip=Dfn.Geoip(**user.get('geoip', {})),
                        tls=Dfn.Tls(**user.get('tls', {})),
                        user=user_model
                    )

            return user_obj

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return Dfn.Client(error=Dfn.RPCErrorModel(-1, ke.__str__()))
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return Dfn.Client(error=Dfn.RPCErrorModel(-1, err.__str__()))

    def set_nick(self, nickoruid: str, newnick: str,
                 force: bool = False) -> Dfn.RPCResult:
        """Sets the nick name of a user (changes the nick).
        force: if set to true then q-lines (banned nick)
        checks will be bypassed. And also,
        if the new nick name already exists, the other existing
        user is killed and we will take that new nick.

        Args:
            nickoruid (str): the nick name or the UID
            newnick (str): the new nick name
            force (bool, optional): q-lines (banned nick)
                checks will be bypassed. Defaults to False.

        Returns:
            bool: True if success else error will be stored in ErrorModel
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                'user.set_nick',
                {'nick': nickoruid, 'newnick': newnick, 'force': force})
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                return response_model

            return response_model

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return Dfn.RPCResult(error=Dfn.RPCErrorModel(-1, ke.__str__()))
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return Dfn.RPCResult(error=Dfn.RPCErrorModel(-1, err.__str__()))

    def set_username(self, nickoruid: str, username: str) -> Dfn.RPCResult:
        """Set the username / ident of a user.

        Args:
            nickoruid (str): the nick name or the UID
            username (str): the new user name / ident

        Returns:
            bool: True if success else error will be stored in ErrorModel
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                'user.set_username',
                {'nick': nickoruid, 'username': username})
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                return response_model

            return response_model

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return Dfn.RPCResult(error=Dfn.RPCErrorModel(-1, ke.__str__()))
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return Dfn.RPCResult(error=Dfn.RPCErrorModel(-1, err.__str__()))

    def set_realname(self, nickoruid: str, realname: str) -> Dfn.RPCResult:
        """Set the realname / gecos of a user.

        Args:
            nickoruid (str): the nick name or the UID
            realname (str):  the new realname / gecos of a user.

        Returns:
            bool: True if success else error will be stored in ErrorModel
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                'user.set_realname',
                {'nick': nickoruid, 'realname': realname})
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                return response_model

            return response_model

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return Dfn.RPCResult(error=Dfn.RPCErrorModel(-1, ke.__str__()))
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return Dfn.RPCResult(error=Dfn.RPCErrorModel(-1, err.__str__()))

    def set_vhost(self, nickoruid: str, vhost: str) -> Dfn.RPCResult:
        """Set a virtual host (vhost) on the user.

        Args:
            nickoruid (str): the nick name or the UID
            vhost (str): the new virtual host.

        Returns:
            bool: True if success else error will be stored in ErrorModel
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                'user.set_vhost',
                {'nick': nickoruid, 'vhost': vhost})
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                return response_model

            return response_model

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return Dfn.RPCResult(error=Dfn.RPCErrorModel(-1, ke.__str__()))
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return Dfn.RPCResult(error=Dfn.RPCErrorModel(-1, err.__str__()))

    def set_mode(self, nickoruid: str, modes: str) -> Dfn.RPCResult:
        """Change the modes of a user.

        Args:
            nickoruid (str): the nick name or the UID
            modes (str): the mode string, eg -i+w

        Returns:
            bool: True if success else error will be stored in ErrorModel
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                'user.set_mode',
                {'nick': nickoruid, 'modes': modes})
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                return response_model

            return response_model

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return Dfn.RPCResult(error=Dfn.RPCErrorModel(-1, ke.__str__()))
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return Dfn.RPCResult(error=Dfn.RPCErrorModel(-1, err.__str__()))

    def set_snomask(self, nickoruid: str, snomask: str) -> Dfn.RPCResult:
        """Change the snomask of a user.

        Args:
            nickoruid (str): the nick name or the UID
            snomask (str): the snomask string, eg -j+R

        Returns:
            bool: True if success else error will be stored in ErrorModel
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                'user.set_snomask',
                {'nick': nickoruid, 'snomask': snomask})
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                return response_model

            return response_model

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return Dfn.RPCResult(error=Dfn.RPCErrorModel(-1, ke.__str__()))
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return Dfn.RPCResult(error=Dfn.RPCErrorModel(-1, err.__str__()))

    def set_oper(self, nickoruid: str, oper_account: str, oper_class: str,
                 class_: str = '', modes: str = '',
                 snomask: str = '', vhost: str = ''
                 ) -> Dfn.RPCResult:
        """Make user an IRC operator.

        Args:
            nickoruid (str): the nick name or the UID
            oper_account (str):  the oper account, to be shown in WHOIS to
                fellow ircops and in logs.
            oper_class (str):
                the operclass. Usually one of the default operclasses like
                netadmin-with-override

            class_ (str, optional): the class to put the user in.
                If this option is not specified then opers is assumed,
                since this class exists in most unrealircd.conf's.
                You can specify "" (empty) if you don't want to put
                the user in a class. Defaults to ''.

            modes (str, optional): user modes to set on oper.
                For example: +xws. If this option is not specified
                then set::modes-on-oper is used. You can specify "" (empty)
                if you don't want to set any additional modes on the user.
                Defaults to ''.

            snomask (str, optional): snomask to set on oper.
                For example: +bBcdfkqsSoO. If this option is not specified
                then set::snomask-on-oper is used. You can specify "" (empty)
                if you don't want to set any snomasks on the user.
                Defaults to ''.

            vhost (str, optional): virtual host to set on oper.
                Defaults to ''.

        Returns:
            bool: True if success else error will be stored in ErrorModel
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                'user.set_oper',
                {'nick': nickoruid, 'oper_account': oper_account,
                 'oper_class': oper_class, 'class': class_,
                 'modes': modes, 'snomask': snomask, 'vhost': vhost})
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                return response_model

            return response_model

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return Dfn.RPCResult(error=Dfn.RPCErrorModel(-1, ke.__str__()))
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return Dfn.RPCResult(error=Dfn.RPCErrorModel(-1, err.__str__()))

    def join(self, nickoruid: str, channel: str, key: str = '',
             force: bool = False) -> Dfn.RPCResult:
        """Join a user to a channel.

        Note: If force is set to true then the user will walk through bans,
        modes and other restrictions (similar to SAJOIN on IRC).
        If force is not set, or set to false, then it will be a regular JOIN
        attempt that may fail.
        If it fails then the user will see an error message on their screen,
        such as for example Cannot join channel (+k).

        Args:
            nickoruid (str): the nick name or the UID
            channel (str): the channel(s) to join
                (e.g. #channel or #channel1,#channel2)
            key (str, optional): the key of the channel(s) (only for channels
                with +k needed, again separate by colon for multiple
                channels). Defaults to ''.
            force (bool, optional): whether to bypass join restrictions
                or not. Defaults to False.

        Returns:
            bool: True if success else error will be stored in ErrorModel
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                'user.join',
                {'nick': nickoruid, 'channel': channel,
                 'key': key, 'force': force})
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                return response_model

            return response_model

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return Dfn.RPCResult(error=Dfn.RPCErrorModel(-1, ke.__str__()))
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return Dfn.RPCResult(error=Dfn.RPCErrorModel(-1, err.__str__()))

    def part(self, nickoruid: str, channel: str,
             force: bool = False) -> Dfn.RPCResult:
        """Part a user from a channel.

        Note: If force is set to true then the user will see a notice that
        they were forcefully PARTed from the channel(s).
        If force is not set, or set to false, then there will be no such
        notice.

        Args:
            nickoruid (str): the nick name or the UID
            channel (str): the channel(s) to join
                (e.g. #channel or #channel1,#channel2)
            force (bool, optional): whether to bypass join restrictions or
                not. Defaults to False.

        Returns:
            bool: True if success else error will be stored in ErrorModel
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                'user.part',
                {'nick': nickoruid, 'channel': channel, 'force': force})
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                return response_model

            return response_model

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return Dfn.RPCResult(error=Dfn.RPCErrorModel(-1, ke.__str__()))
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return Dfn.RPCResult(error=Dfn.RPCErrorModel(-1, err.__str__()))

    def kill(self, nickoruid: str, reason: str) -> Dfn.RPCResult:
        """Kill a user, showing that the user was forcefully removed.

        Note: There is also user.quit. The difference is that user.kill will
        show that the user is forcefully killed, while user.quit pretend the
        user quit normally.
        This slight difference may invoke certain client behavior.
        For example, some clients don't immediately reconnect
        for a KILL but do so on a QUIT.

        Args:
            nickoruid (str): the nick name or the UID
            reason (str): reason for the kill

        Returns:
            bool: True if success else error will be stored in ErrorModel
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                'user.kill',
                {'nick': nickoruid, 'reason': reason})
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                return response_model

            return response_model

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return Dfn.RPCResult(error=Dfn.RPCErrorModel(-1, ke.__str__()))
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return Dfn.RPCResult(error=Dfn.RPCErrorModel(-1, err.__str__()))

    def quit(self, nickoruid: str, reason: str) -> Dfn.RPCResult:
        """Quit a user, pretending it was a normal QUIT.

        Note: There is also user.kill. The difference is that user.kill
        will show that the user is forcefully killed,
        while user.quit pretend the user quit normally.
        This slight difference may invoke certain client behavior.
        For example, some clients don't immediately reconnect for a KILL but
        do so on a QUIT.

        Args:
            nickoruid (str): the nick name or the UID
            reason (str): reason for the kill

        Returns:
            bool: True if success else error will be stored in ErrorModel
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                'user.quit',
                {'nick': nickoruid, 'reason': reason})
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                return response_model

            return response_model

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return Dfn.RPCResult(error=Dfn.RPCErrorModel(-1, ke.__str__()))
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return Dfn.RPCResult(error=Dfn.RPCErrorModel(-1, err.__str__()))

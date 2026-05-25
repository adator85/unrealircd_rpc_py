from typing import TYPE_CHECKING, Literal
import unrealircd_rpc_py.objects.Definition as Dfn
from unrealircd_rpc_py.utils import utils

if TYPE_CHECKING:
    from unrealircd_rpc_py.connections.sync.IConnection import IConnection


class Channel:

    DB_CHANNELS: list[Dfn.Channel] = []

    def __init__(self, connection: 'IConnection') -> None:

        # Get the Connection instance
        self.Connection = connection
        self.Logs = connection.Logs

    def list_(self, object_detail_level: Literal[0, 1, 2, 3, 4] = 1
              ) -> list[Dfn.Channel]:
        """List channels.

        if you want to have more details increase the level or see the level
        you want by visiting this page:

        https://www.unrealircd.org/docs/JSON-RPC:Channel#Structure_of_a_channel

        Args:
            object_detail_level (int, optional): set the detail of the
                response object, see the Detail level column in Structure
                of a channel.
                In this RPC call it defaults to 1 if this parameter is not
                specified. Defaults to 1.

        Returns:
            Channel: List of Channel object, None if nothing see the
                Error property
        """
        try:
            self.DB_CHANNELS = []
            response: dict[str, dict] = self.Connection.query(
                method='channel.list',
                param={'object_detail_level': object_detail_level}
            )
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                self.DB_CHANNELS.append(
                    Dfn.Channel(error=response_model.error)
                )
                return self.DB_CHANNELS

            channels: list[dict] = response_model.result.get('list', [])

            for channel in channels:
                channel_copy: dict = channel.copy()

                for key in ['bans', 'ban_exemptions', 'invite_exceptions',
                            'members']:
                    channel_copy.pop(key, None)

                self.DB_CHANNELS.append(
                        Dfn.Channel(
                            **channel_copy,
                            bans=[
                                Dfn.ChannelBans(**ban) for ban in
                                channel.get('bans', [])],
                            ban_exemptions=[
                                Dfn.ChannelBanExemptions(**ban_ex)
                                for ban_ex in channel.get(
                                    'ban_exemptions', [])
                            ],
                            invite_exceptions=[
                                Dfn.ChannelInviteExceptions(**inv_ex)
                                for inv_ex in channel.get(
                                    'invite_exceptions', [])
                            ],
                            members=[
                                Dfn.ChannelMembers(**member)
                                for member in channel.get('members', [])
                            ]
                        )
                )

            return self.DB_CHANNELS

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return []
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return []

    def get(self, channel: str, object_detail_level: int = 3) -> Dfn.Channel:
        """Retrieve all details of a single channel.
        This returns more information than a channel.list call, see the end
        of Structure of a channel.

        Args:
            channel (str):  the name of the channel
            object_detail_level (int, optional): set the detail of the
                response object, see the Detail level column in Structure of
                a channel. In this RPC call it defaults to 3 if this parameter
                is not specified. Defaults to 3.

        Returns:
            Channel: The Channel Object, None if nothing see Error property
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                method='channel.get',
                param={'channel': channel,
                       'object_detail_level': object_detail_level})
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                return Dfn.Channel(error=response_model.error)

            channel: dict = response_model.result.get('channel', {})

            channel_copy: dict = channel.copy()
            for key in ['bans', 'ban_exemptions', 'invite_exceptions',
                        'members']:
                channel_copy.pop(key, None)

            members: list[dict] = channel.get('members', [])
            db_members: list[Dfn.ChannelMembers] = []

            for member in members:
                user_dict: dict[str, dict] = member.get(
                    'user', Dfn.User().to_dict()
                )
                tls_dict: dict[str, dict] = member.get(
                    'tls', Dfn.Tls().to_dict()
                )
                geoip_dict: dict[str, dict] = member.get(
                    'geoip', Dfn.Geoip().to_dict()
                )

                if 'security-groups' in user_dict:
                    # rename key
                    user_dict['security_groups'] = user_dict.pop(
                        'security-groups'
                    )

                if 'country-code' in geoip_dict:
                    geoip_dict['country_code'] = geoip_dict.pop(
                        'country-code'
                    )

                for key in ['user', 'tls', 'geoip']:
                    member.pop(key, None)

                user_obj = Dfn.User(**user_dict)
                tls_obj = Dfn.Tls(**tls_dict)
                geoip_obj = Dfn.Geoip(**geoip_dict)

                member_obj = Dfn.ChannelMembers(**member,
                                                user=user_obj,
                                                tls=tls_obj,
                                                geoip=geoip_obj)

                db_members.append(member_obj)

            channel_obj = Dfn.Channel(
                        **channel_copy,
                        bans=[
                            Dfn.ChannelBans(**ban)
                            for ban in channel.get('bans', [])
                        ],
                        ban_exemptions=[
                            Dfn.ChannelBanExemptions(**ban_ex)
                            for ban_ex in channel.get('ban_exemptions', [])
                        ],
                        invite_exceptions=[
                            Dfn.ChannelInviteExceptions(**inv_ex)
                            for inv_ex in channel.get('invite_exceptions', [])
                        ],
                        # members=[Dfn.ChannelMembers(**member)
                        # for member in channel.get('members', [])]
                        members=db_members
                    )

            return channel_obj

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return Dfn.Channel(error=Dfn.RPCErrorModel(-1, ke.__str__()))
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return Dfn.Channel(error=Dfn.RPCErrorModel(-1, err.__str__()))

    def set_mode(self, channel: str, modes: str, parameters: str = ""
                 ) -> Dfn.RPCResult:
        """Set and unset modes on a channel.

        Args:
            channel (str): The name of the channel
            modes (str): The mode(s) to change, eg +be
            parameters (str): The parameters, eg some!nice@ban some!nice@invex

        Returns:
            bool: True if success
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                method='channel.set_mode',
                param={"channel": channel, "modes": modes,
                       "parameters": parameters}
            )
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

    def set_topic(self, channel: str, topic: str, set_by: str = None,
                  set_at: str = None) -> Dfn.RPCResult:
        """Set a topic on a channel.

        Args:
            channel (str): The name of the channel
            topic (str): The new topic
            set_by (str, optional): who set the topic
                (but, see important note below). Defaults to None.
            set_at (str, optional): when the topic was set (timestamp).
                Defaults to None.

        Returns:
            bool: True if success
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                method='channel.set_topic',
                param={"channel": channel, "topic": topic, "set_by": set_by,
                       "set_at": set_at}
            )
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

    def kick(self, channel: str, nick: str, reason: str) -> Dfn.RPCResult:
        """Kick a user from a channel

        Args:
            channel (str): The name of the channel
            nick (str): The user to kick
            reason (str): The kick reason (shown in the channel)

        Returns:
            bool: True if success
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                method='channel.kick',
                param={"channel": channel, "nick": nick, "reason": reason}
            )
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

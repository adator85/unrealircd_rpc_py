import traceback
from types import SimpleNamespace
from typing import Union
from unrealircd_rpc_py.Connection import Connection
import unrealircd_rpc_py.Definition as dfn

class Channel:

    DB_CHANNELS: list[dfn.Channel] = []

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

    def list_(self, _object_detail_level: int = 1) -> Union[list[dfn.Channel], None]:
        """List channels.

        if you want to have more details increase the level or see the level you want by visiting this page:

        https://www.unrealircd.org/docs/JSON-RPC:Channel#Structure_of_a_channel

        Args:
            _object_detail_level (int, optional): set the detail of the response object, see the Detail level column in Structure of a channel. In this RPC call it defaults to 1 if this parameter is not specified. Defaults to 1.

        Returns:
            Channel: List of Channel object, None if nothing see the Error property
        """
        try:
            self.DB_CHANNELS = []
            response = self.Connection.query(method='channel.list', param={'object_detail_level': _object_detail_level})

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

            channels: list[dict] = response['result']['list']

            for channel in channels:
                channel_copy: dict = channel.copy()

                for key in ['bans','ban_exemptions','invite_exceptions', 'members']:
                    channel_copy.pop(key, None)

                self.DB_CHANNELS.append(
                        dfn.Channel(
                            **channel_copy,
                            bans=[dfn.ChannelBans(**ban) for ban in channel.get('bans', [])],
                            ban_exemptions=[dfn.ChannelBanExemptions(**ban_ex) for ban_ex in channel.get('ban_exemptions', [])],
                            invite_exceptions=[dfn.ChannelInviteExceptions(**inv_ex) for inv_ex in channel.get('invite_exceptions', [])],
                            members=[dfn.ChannelMembers(**member) for member in channel.get('members', [])]
                        )
                )

            return self.DB_CHANNELS

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            self.Logs.error(traceback.format_exc())

    def get(self, channel: str, _object_detail_level: int = 3) -> Union[dfn.Channel, None]:
        """Retrieve all details of a single channel. 
        This returns more information than a channel.list call, see the end of Structure of a channel.

        Args:
            channel (str):  the name of the channel
            _object_detail_level (int, optional): set the detail of the response object, see the Detail level column in Structure of a channel. In this RPC call it defaults to 3 if this parameter is not specified. Defaults to 3.

        Returns:
            Channel: The Channel Object, None if nothing see Error property
        """
        try:
            response = self.Connection.query(method='channel.get', param={'channel': channel, 'object_detail_level': _object_detail_level})

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

            channel: dict = response['result']['channel']

            channel_copy: dict = channel.copy()
            for key in ['bans','ban_exemptions','invite_exceptions', 'members']:
                    channel_copy.pop(key, None)

            objectChannel = dfn.Channel(
                        **channel_copy,
                        bans=[dfn.ChannelBans(**ban) for ban in channel.get('bans', [])],
                        ban_exemptions=[dfn.ChannelBanExemptions(**ban_ex) for ban_ex in channel.get('ban_exemptions', [])],
                        invite_exceptions=[dfn.ChannelInviteExceptions(**inv_ex) for inv_ex in channel.get('invite_exceptions', [])],
                        members=[dfn.ChannelMembers(**member) for member in channel.get('members', [])]
                    )

            return objectChannel

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
        except Exception as err:
            self.Logs.error(f'General error: {err}')

    def set_mode(self, channel: str, modes: str, parameters: str) -> bool:
        """Set and unset modes on a channel.

        Args:
            channel (str): The name of the channel
            modes (str): The mode(s) to change, eg +be
            parameters (str): The parameters, eg some!nice@ban some!nice@invex

        Returns:
            bool: True if success
        """
        try:
            response = self.Connection.query(method='channel.set_mode', param={"channel": channel,"modes": modes,"parameters": parameters})

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

            return True

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
        except Exception as err:
            self.Logs.error(f'General error: {err}')

    def set_topic(self, channel: str, topic: str, _set_by: str = None, _set_at: str = None) -> bool:
        """Set a topic on a channel.

        Args:
            channel (str): The name of the channel
            topic (str): The new topic
            _set_by (str, optional): who set the topic (but, see important note below). Defaults to None.
            _set_at (str, optional): when the topic was set (timestamp). Defaults to None.

        Returns:
            bool: True if success
        """
        try:
            response = self.Connection.query(method='channel.set_topic', param={"channel": channel, "topic": topic, "set_by": _set_by, "set_at": _set_at})

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

            return True

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
        except Exception as err:
            self.Logs.error(f'General error: {err}')

    def kick(self, channel: str, nick: str, reason: str) -> bool:
        """Kick a user from a channel

        Args:
            channel (str): The name of the channel
            nick (str): The user to kick
            reason (str): The kick reason (shown in the channel)

        Returns:
            bool: True if success
        """
        try:
            response = self.Connection.query(method='channel.kick', param={"channel": channel, "nick": nick, "reason": reason})

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

            return True

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
        except Exception as err:
            self.Logs.error(f'General error: {err}')
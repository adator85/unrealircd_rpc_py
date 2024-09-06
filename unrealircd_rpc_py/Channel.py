from typing import Union
from dataclasses import dataclass
from unrealircd_rpc_py.Connection import Connection

class Channel:

    @dataclass
    class ModelChannel:
        name: str
        creation_time: str
        num_users: int
        topic: str
        topic_set_by: str
        topic_set_at: str
        modes: str
        bans: list
        ban_exemptions: list
        invite_exceptions: list
        members: list

    DB_CHANNELS: list[ModelChannel] = []


    def __init__(self, Connection: Connection) -> None:

        # Record the original response
        self.original_response: str = ''

        # Get the Connection instance
        self.Connection = Connection
        self.Logs = Connection.Logs
        self.Error = Connection.Error

    def list_(self, _object_detail_level: int = 1) -> Union[list[ModelChannel], None, bool]:
        """List channels.

        Args:
            _object_detail_level (int, optional): set the detail of the response object, see the Detail level column in Structure of a channel. In this RPC call it defaults to 1 if this parameter is not specified. Defaults to 1.

        Returns:
            Union[list[ModelChannel], None, bool]: List of ModelChannel, None if nothing or False if error
        """
        try:
            response = self.Connection.query(method='channel.list', param={'object_detail_level': _object_detail_level})
            self.original_response = response

            if response is None:
                return False

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.set_error(response)
                return False

            channels = response['result']['list']

            for channel in channels:
                self.DB_CHANNELS.append(
                        self.ModelChannel(
                            name=channel['name'] if 'name' in channel else None,
                            creation_time=channel['creation_time'] if 'creation_time' in channel else None,
                            num_users=channel['num_users'] if 'num_users' in channel else 0,
                            topic=channel['topic'] if 'topic' in channel else None,
                            topic_set_by=channel['topic_set_by'] if 'topic_set_by' in channel else None,
                            topic_set_at=channel['topic_set_at'] if 'topic_set_at' in channel else None,
                            modes=channel['modes'] if 'modes' in channel else None,
                            bans=channel['bans'] if 'bans' in channel else [],
                            ban_exemptions=channel['ban_exemptions'] if 'ban_exemptions' in channel else [],
                            invite_exceptions=channel['invite_exceptions'] if 'invite_exceptions' in channel else [],
                            members=channel['members'] if 'members' in channel else []
                        )
                )

            return self.DB_CHANNELS

        except KeyError as ke:
            self.Logs.error(ke)
        except Exception as err:
            self.Logs.error(err)

    def get(self, channel: str, _object_detail_level: int = 3) -> Union[ModelChannel, None, bool]:
        """Retrieve all details of a single channel. 
        This returns more information than a channel.list call, see the end of Structure of a channel.

        Args:
            channel (str):  the name of the channel
            _object_detail_level (int, optional): set the detail of the response object, see the Detail level column in Structure of a channel. In this RPC call it defaults to 3 if this parameter is not specified. Defaults to 3.

        Returns:
            Union[ModelChannel, None, bool]: ModelChannel, None if nothing or False if error
        """
        try:
            response = self.Connection.query(method='channel.get', param={'channel': channel, 'object_detail_level': _object_detail_level})
            self.original_response = response

            if response is None:
                return False

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.set_error(response)
                return False

            channel = response['result']['channel']

            objectChannel = self.ModelChannel(
                            name=channel['name'] if 'name' in channel else None,
                            creation_time=channel['creation_time'] if 'creation_time' in channel else None,
                            num_users=channel['num_users'] if 'num_users' in channel else 0,
                            topic=channel['topic'] if 'topic' in channel else None,
                            topic_set_by=channel['topic_set_by'] if 'topic_set_by' in channel else None,
                            topic_set_at=channel['topic_set_at'] if 'topic_set_at' in channel else None,
                            modes=channel['modes'] if 'modes' in channel else None,
                            bans=channel['bans'] if 'bans' in channel else [],
                            ban_exemptions=channel['ban_exemptions'] if 'ban_exemptions' in channel else [],
                            invite_exceptions=channel['invite_exceptions'] if 'invite_exceptions' in channel else [],
                            members=channel['members'] if 'members' in channel else []
                        )

            return objectChannel

        except KeyError as ke:
            self.Logs.error(ke)
        except Exception as err:
            self.Logs.error(err)

    def set_mode(self, channel: str, modes: str, parameters: str) -> bool:
        """Set and unset modes on a channel.

        Args:
            channel (str): The name of the channel
            modes (str): The mode(s) to change, eg +be
            parameters (str): The parameters, eg some!nice@ban some!nice@invex

        Returns:
            bool: True if success
        """
        response = self.Connection.query(method='channel.set_mode', param={"channel": channel,"modes": modes,"parameters": parameters})
        self.original_response = response

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
        response = self.Connection.query(method='channel.set_topic', param={"channel": channel, "topic": topic, "set_by": _set_by, "set_at": _set_at})
        self.original_response = response

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

    def kick(self, channel: str, nick: str, reason: str) -> bool:
        """Kick a user from a channel

        Args:
            channel (str): The name of the channel
            nick (str): The user to kick
            reason (str): The kick reason (shown in the channel)

        Returns:
            bool: True if success
        """

        response = self.Connection.query(method='channel.kick', param={"channel": channel, "nick": nick, "reason": reason})
        self.original_response = response

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
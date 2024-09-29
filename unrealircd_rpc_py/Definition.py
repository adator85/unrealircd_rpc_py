from dataclasses import dataclass, field

@dataclass
class RPCError:
    """This model will contain the error if any"""
    code: int = 0
    message: str = None

@dataclass
class Tls:
    certfp: str = None
    cipher: str = None

@dataclass
class Geoip:
    country_code: str = None
    asn: str = None
    asname: str = None

@dataclass
class UserChannel:
    name: str = None
    level: str = None

@dataclass
class User:
    username: str = None
    realname: str = None
    vhost: str = None
    cloakedhost: str = None
    servername: str = None
    account: str = None
    reputation: int = None
    security_groups: list[str] = field(default_factory=list)
    modes: str = None
    snomasks: str = None
    operlogin: str = None
    operclass: str = None
    channels: list[UserChannel] = field(default_factory=list[UserChannel])

@dataclass
class Client:
    name: str = None
    id: str = None
    hostname: str = None
    ip: str = None
    details: str = None
    geoip: Geoip = field(default_factory=Geoip)
    server_port: int = 0
    client_port: int = 0
    connected_since: str = None
    idle_since: str = None
    tls: Tls = field(default_factory=Tls)
    user: User = field(default_factory=User)

@dataclass
class ServerModule:
    name: str = None
    version: str = None
    author: str = None
    description: str = None
    third_party: bool = False
    permanent: bool = False
    permanent_but_reloadable: bool = False

@dataclass
class ServerRehashClient:
    name: str = None
    id: str = None
    hostname: str = None
    ip: str = None
    server_port: int = 0
    details: str = None
    connected_since: str = None
    idle_since: str = None

@dataclass
class ServerRehashLogSource:
    file: str = None
    line: int = 0
    function: str = None

@dataclass
class ServerRehashLog:
    timestamp: str = None
    level: str = None
    subsystem: str = None
    event_id: str = None
    log_source: str = None
    msg: str = None
    source: ServerRehashLogSource = field(default_factory=ServerRehashLogSource)

@dataclass
class ServerRehash:
    rehash_client: ServerRehashClient = field(default_factory=ServerRehashClient)
    log: list[ServerRehashLog] = field(default_factory=list[ServerRehashLog])
    success: str = None

@dataclass
class ServerRpcModules:
    name: str = None
    version: str = None

@dataclass
class ServerFeatures:
    software: str = None
    protocol: int = 0
    usermodes: str = None
    chanmodes: list[str] = field(default_factory=list)
    nick_character_sets: str = None
    rpc_modules: list[ServerRpcModules] = field(default_factory=list[ServerRpcModules])

@dataclass
class Server:
    info: str = None
    uplink: str = None
    num_users: int = 0
    boot_time: str = None
    synced: bool = False
    ulined: bool = False
    features: ServerFeatures = field(default_factory=ServerFeatures)

@dataclass
class ClientServer:
    name: str = None
    id: str = None
    hostname: str = None
    ip: str = None
    details: str = None
    server_port: int = 0
    client_port: int = 0
    connected_since: str = None
    idle_since: str = None
    server: Server = field(default_factory=Server)
    tls: Tls = field(default_factory=Tls)

@dataclass
class ChannelBans:
    name: str = None
    set_by: str = None
    set_at: str = None

@dataclass
class ChannelBanExemptions:
    name: str = None
    set_by: str = None
    set_at: str = None

@dataclass
class ChannelInviteExceptions:
    name: str = None
    set_by: str = None
    set_at: str = None

@dataclass
class ChannelMembers:
    level: str = None
    name: str = None
    id: str = None
    hostname: str = None
    ip: str = None
    details: str = None
    geoip: Geoip = field(default_factory=Geoip)

@dataclass
class Channel:
    name: str = None
    creation_time: str = None
    num_users: int = 0
    topic: str = None
    topic_set_by: str = None
    topic_set_at: str = None
    modes: str = None
    bans: list[ChannelBans] = field(default_factory=list[ChannelBans])
    ban_exemptions: list[ChannelBanExemptions] = field(default_factory=list[ChannelBanExemptions])
    invite_exceptions: list[ChannelInviteExceptions] = field(default_factory=list[ChannelInviteExceptions])
    members: list[ChannelMembers] = field(default_factory=list[ChannelMembers])

@dataclass
class NameBan:
    type: str = None
    type_string: str = None
    set_by: str = None
    set_at: str = None
    expire_at: str = None
    set_at_string: str = None
    expire_at_string: str = None
    duration_string: str = None
    set_at_delta: int = 0
    set_in_config: bool = False
    name: str = None
    reason: str = None

@dataclass
class ServerBan:
    type: str = None
    type_string: str = None
    set_by: str = None
    set_at: str = None
    expire_at: str = None
    set_at_string: str = None
    expire_at_string: str = None
    duration_string: str = None
    set_at_delta: int = 0
    set_in_config: bool = False
    name: str = None
    reason: str = None

@dataclass
class ServerBanException:
    type: str = None
    type_string: str = None
    set_by: str = None
    set_at: str = None
    expire_at: str = None
    set_at_string: str = None
    expire_at_string: str = None
    duration_string: str = None
    set_at_delta: int = None
    set_in_config: bool = False
    name: str = None
    reason: str = None
    exception_types: str = None

@dataclass
class Spamfilter:
    type: str = None
    type_string: str = None
    set_by: str = None
    set_at: str = None
    expire_at: str = None
    set_at_string: str = None
    expire_at_string: str = None
    duration_string: str = None
    set_at_delta: int = 0
    set_in_config: bool = False
    name: str = None
    match_type: str = None
    ban_action: str = None
    ban_duration: int = 0
    ban_duration_string: str = None
    spamfilter_targets: str = None
    reason: str = None
    hits: int = 0
    hits_except: int = 0

@dataclass
class RpcInfo:
    name: str = None
    module: str = None
    version: str = None
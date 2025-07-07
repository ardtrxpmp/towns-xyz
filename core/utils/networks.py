from dataclasses import dataclass


class Network:

    def __init__(
        self,
        name,
        chain_id,
        rpc_list,
        scanner,
        eip1559_support: bool = False,
        token: str = "ETH",
    ):
        self.name = name
        self.chain_id = chain_id
        self.rpc_list = rpc_list
        self.scanner = scanner
        self.token = token


@dataclass
class Networks:
    Ethereum = Network(
        name="Ethereum",
        chain_id=1,
        rpc_list=[
            "https://eth.meowrpc.com",
            "https://eth.drpc.org",
        ],
        scanner="https://etherscan.io",
        eip1559_support=True,
    )
    Base = Network(
        name="Base",
        chain_id=8453,
        rpc_list=[
            "https://damp-ultra-spree.base-mainnet.quiknode.pro/61a953d960f44f9c2661db41a1ec2c57b699dde8",
            "https://damp-ultra-spree.base-mainnet.quiknode.pro/61a953d960f44f9c2661db41a1ec2c57b699dde8",
        ],
        scanner="https://basescan.org",
        eip1559_support=True,
    )

    NetworkList = [Ethereum, Base]

    @staticmethod
    def get_network_by_name(name: str) -> Network | None:
        return {
            "Ethereum": Networks.Ethereum,
            "Base": Networks.Base,
        }.get(name, None)

    @staticmethod
    def get_network_by_orbiter_id(orbiter_id: int) -> Network | None:
        return Networks.get_network_by_name(
            {
                1: "Ethereum",
                21: "Base",
            }.get(orbiter_id, None)
        )

    @staticmethod
    def get_network_by_chain_id(chain_id: int) -> Network | None:
        return {
            1: Networks.Ethereum,
            8453: Networks.Base,
        }.get(chain_id, None)

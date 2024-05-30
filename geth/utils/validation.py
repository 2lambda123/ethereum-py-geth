from __future__ import (
    annotations,
)

from typing import (
    Any,
    Literal,
)

from pydantic import (
    BaseModel,
    ConfigDict,
    ValidationError,
)

from geth.exceptions import (
    PyGethValueError,
)
from geth.types import (
    GenesisDataTypedDict,
    GethKwargsTypedDict,
)


class GethKwargs(BaseModel):
    allow_insecure_unlock: bool | None = None
    autodag: bool | None = False
    cache: int | None = None
    data_dir: str | None = None
    dev_mode: bool | None = False
    gcmode: Literal["full", "archive"] | None = None
    geth_executable: str | None = None
    ipc_disable: bool | None = None
    ipc_path: str | None = None
    max_peers: str | None = None
    mine: bool | None = False
    miner_etherbase: int | None = None
    network_id: str | None = None
    nice: bool | None = True
    no_discover: bool | None = None
    password: bytes | str | None = None
    port: str | None = None
    preload: str | None = None
    rpc_addr: str | None = None
    rpc_api: str | None = None
    rpc_cors_domain: str | None = None
    rpc_enabled: bool | None = None
    rpc_port: str | None = None
    shh: bool | None = None
    stdin: str | None = None
    suffix_args: list[str] | None = None
    suffix_kwargs: dict[str, Any] | None = None
    tx_pool_global_slots: int | None = None
    tx_pool_price_limit: int | None = None
    unlock: str | None = None
    verbosity: int | None = None
    ws_addr: str | None = None
    ws_api: str | None = None
    ws_enabled: bool | None = None
    ws_origins: str | None = None
    ws_port: str | None = None

    model_config = ConfigDict(extra="forbid")


def validate_geth_kwargs(geth_kwargs: GethKwargsTypedDict) -> bool:
    """
    Converts geth_kwargs to GethKwargs and raises a ValueError if the conversion fails.
    """
    try:
        GethKwargs(**geth_kwargs)
    except ValidationError as e:
        raise PyGethValueError(f"geth_kwargs validation failed: {e}")
    except TypeError as e:
        raise PyGethValueError(f"error while validating geth_kwargs: {e}")
    return True


class GenesisDataConfig(BaseModel):
    ethash: dict[str, Any] = {}
    homesteadBlock: int = 0
    daoForkBlock: int = 0
    daoForkSupport: bool = True
    eip150Block: int = 0
    eip155Block: int = 0
    eip158Block: int = 0
    byzantiumBlock: int = 0
    constantinopleBlock: int = 0
    petersburgBlock: int = 0
    istanbulBlock: int = 0
    berlinBlock: int = 0
    londonBlock: int = 0
    arrowGlacierBlock: int = 0
    grayGlacierBlock: int = 0
    # merge
    terminalTotalDifficulty: int = 0
    terminalTotalDifficultyPassed: bool = True
    # post-merge, timestamp is used for network transitions
    shanghaiTime: int = 0
    cancunTime: int = 0

    model_config = ConfigDict(extra="forbid")


class GenesisData(BaseModel):
    alloc: dict[str, dict[str, Any]] = {}
    coinbase: str = "0x3333333333333333333333333333333333333333"
    config: dict[str, Any] = GenesisDataConfig().model_dump()
    difficulty: str = "0x0"
    extraData: str = (
        "0x0000000000000000000000000000000000000000000000000000000000000000"
    )
    gasLimit: str = "0x47e7c4"
    mixhash: str = "0x0000000000000000000000000000000000000000000000000000000000000000"
    nonce: str = "0x0"
    parentHash: str = (
        "0x0000000000000000000000000000000000000000000000000000000000000000"
    )
    timestamp: str = "0x0"

    model_config = ConfigDict(extra="forbid")


def validate_genesis_data(genesis_data: GenesisDataTypedDict) -> bool:
    """
    Validates the genesis data config field
    """
    genesis_data_config = genesis_data.get("config", None)
    if genesis_data_config:
        try:
            GenesisDataConfig(**genesis_data_config)
        except ValidationError as e:
            raise PyGethValueError(f"genesis_data config field validation failed: {e}")
        except TypeError as e:
            raise PyGethValueError(
                f"error while validating genesis_data config field: {e}"
            )
    """
    Validates the genesis data
    """
    try:
        GenesisData(**genesis_data)
    except ValidationError as e:
        raise PyGethValueError(f"genesis_data validation failed: {e}")
    except TypeError as e:
        raise PyGethValueError(f"error while validating genesis_data: {e}")
    return True

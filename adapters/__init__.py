from adapters.generic import GenericAdapter
from adapters.hdfc import HDFCAdapter
from adapters.sbi import SBIAdapter
from adapters.jkb import JKBAdapter


def get_adapter(bank):
    if bank == "HDFC":
        return HDFCAdapter()
    if bank == "SBI":
        return SBIAdapter()
    if bank == "JKB":
        return JKBAdapter()
    return GenericAdapter()

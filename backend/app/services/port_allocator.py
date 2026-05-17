# ROLE:
# Network port allocation service.
#
# RESPONSIBILITIES:
# - Allocate free ports for deployed services.
#
# MUST NOT:
# - Persist state.
# - Configure proxy or routing.
# - Make deployment decisions.

import socket


def allocate_port() -> int:
    """
    Ask the OS for an available local TCP port.
    """

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]

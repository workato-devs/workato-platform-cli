import contextlib

from collections.abc import AsyncGenerator
from typing import Any

import pytest
import pytest_asyncio

from workato_platform_cli import Workato


@pytest_asyncio.fixture(autouse=True)
async def close_workato_clients(
    monkeypatch: pytest.MonkeyPatch,
) -> AsyncGenerator[None, None]:
    clients: list[Workato] = []
    original_init = Workato.__init__

    def tracking_init(self: Workato, *args: Any, **kwargs: Any) -> None:
        original_init(self, *args, **kwargs)
        clients.append(self)

    monkeypatch.setattr(Workato, "__init__", tracking_init)

    yield

    for client in clients:
        with contextlib.suppress(Exception):
            await client.close()

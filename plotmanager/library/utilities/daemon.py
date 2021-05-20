import asyncio
import logging

from typing import Any, Dict

from chia.daemon.client import DaemonProxy, connect_to_daemon_and_validate
from chia.util.default_root import DEFAULT_ROOT_PATH
from chia.util.ws_message import WsRpcMessage


class DaemonPlotterProxy(DaemonProxy):
    async def start_plotting(self, request: Dict[str, Any]) -> WsRpcMessage:
        data = {"service": "chia plots create"}
        data.update(request)
        request = self.format_request("start_plotting", data)
        response = await self._get(request)
        return response


async def connect_to_daemon_async():
    logging.info(f'Waiting for daemon to be reachable')

    client = None
    while client is None:
        client = await connect_to_daemon_and_validate(DEFAULT_ROOT_PATH)
        if client is None:
            await asyncio.sleep(3)

    client.__class__ = DaemonPlotterProxy
    return client


async def start_plotting_async(daemon, queue, size, memory_buffer, temporary_directory, temporary2_directory,
									destination_directory, threads, buckets, bitfield) -> WsRpcMessage:
	return await daemon.start_plotting({
		"queue": queue,
		"k": size,
		"t": temporary_directory,
		"t2": temporary2_directory,
		"d": destination_directory,
		"b": memory_buffer,
		"u": buckets,
		"r": threads,
		"e": not bitfield,
		"x": False,
		"overrideK": False,
		"parallel": True
	})

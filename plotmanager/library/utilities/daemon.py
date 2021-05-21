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


async def start_plotting_async(queue, size, memory_buffer, temporary_directory, temporary2_directory,
                            destination_directory, threads, buckets, bitfield, exclude_final_directory) -> WsRpcMessage:
    logging.info(f'Waiting for daemon to be reachable')

    client = None
    while client is None:
        try:
            client = await connect_to_daemon_and_validate(DEFAULT_ROOT_PATH)
        except ConnectionAbortedError as e:
            logging.error(f'Connection aborted when connecting to daemon')
        if client is None:
            await asyncio.sleep(3)

    client.__class__ = DaemonPlotterProxy

    result = await client.start_plotting({
        "queue": queue,
        "k": size,
        "t": temporary_directory,
        "t2": temporary2_directory if temporary2_directory else temporary_directory,
        "d": destination_directory,
        "b": memory_buffer,
        "u": buckets,
        "r": threads,
        "e": not bitfield,
        "x": exclude_final_directory,
        "overrideK": False,
        "parallel": True
    })

    await client.close()

    return result

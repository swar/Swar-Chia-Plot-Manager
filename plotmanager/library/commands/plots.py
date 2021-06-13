import logging


def create(*args, chia_location='chia', backend='chia', **kwargs):
    backend_command = _get_backend_command(backend, chia_location)
    backend_flags = _get_backend_flags(backend, *args, **kwargs)

    for key, value in backend_flags.items():
        flag = f'-{key}'
        backend_command.append(flag)
        if value == '':
            continue
        backend_command.append(str(value))

    return backend_command


def _get_backend_command(backend, chia_location):
    logging.debug(f'Parsing backend commands for {backend}')

    backend_commands = dict(
        chia=[chia_location, 'plots', 'create'],
        madmax=[chia_location],
    )

    return backend_commands.get(backend)


def _get_backend_flags(backend, *args, **kwargs):
    logging.debug(f'Parsing backend flags for {backend}')

    backend_parsers = dict(
        chia=_get_chia_flags,
        madmax=_get_madmax_flags,
    )
    backend_parser = backend_parsers.get(backend)

    return backend_parser(*args, **kwargs)


def _get_chia_flags(size, memory_buffer, temporary_directory, destination_directory, threads, buckets, bitfield,
                    temporary2_directory=None, farmer_public_key=None, pool_public_key=None,
                    exclude_final_directory=False):
    flags = dict(
        k=size,
        b=memory_buffer,
        t=temporary_directory,
        d=destination_directory,
        r=threads,
        u=buckets,
    )

    if temporary2_directory is not None:
        flags['2'] = temporary2_directory
    if farmer_public_key is not None:
        flags['f'] = farmer_public_key
    if pool_public_key is not None:
        flags['p'] = pool_public_key
    if bitfield is False:
        flags['e'] = ''
    if exclude_final_directory:
        flags['x'] = ''

    return flags


def _get_madmax_flags(temporary_directory, destination_directory, threads, buckets,
                      temporary2_directory=None, farmer_public_key=None, pool_public_key=None, **kwargs):
    flags = dict(
        r=threads,
        t=temporary_directory,
        d=destination_directory,
        u=buckets,
    )

    if temporary2_directory is not None:
        flags['2'] = temporary2_directory
    if farmer_public_key is not None:
        flags['f'] = farmer_public_key
    if pool_public_key is not None:
        flags['p'] = pool_public_key

    return flags

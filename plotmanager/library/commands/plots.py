def create(size, memory_buffer, temporary_directory, temporary2_directory, destination_directory, threads, buckets, bitfield,
           chia_location='chia'):
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
    if bitfield is False:
        flags['e'] = ''

    data = [chia_location, 'plots', 'create']
    for key, value in flags.items():
        flag = f'-{key}'
        data.append(flag)
        if value == '':
            continue
        data.append(str(value))
    return data

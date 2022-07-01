import esileapclient.tests.functional.utils.output_utils as utils


def _execute(client, cmd, valid_flags, kwargs, args, parse, fail_ok):
    flag_str = utils.kwargs_to_flags(valid_flags, kwargs) if kwargs else ''
    # Cinder will raise an error if subcommand-specific flags are specified
    # before the command itself, so this is necessary
    arg_str = flag_str if not len(args) else ' '.join((flag_str,) + args)
    output = client.cinder(cmd, '', arg_str, fail_ok)
    if parse:
        return utils.parse_cli_output(output) 
    else:
        return output


def volume_create(client, size, parse=True, fail_ok=False, **kwargs):
    valid_flags = ('consisgroup_id', 'group_id', 'snapshot_id', 'source_volid',
                   'image_id', 'image', 'backup_id', 'name', 'description',
                   'volume_type', 'availability_zone', 'metadata', 'hint',
                   'poll')
    # tempest wants this to be a string
    size = str(size)
    return _execute(client, cmd='create', valid_flags=valid_flags,
                    kwargs=kwargs, args=(size,), parse=parse, fail_ok=fail_ok)


def volume_delete(client, volume, fail_ok=False, **kwargs):
    return _execute(client, cmd='delete', valid_flags=('cascade'),
                    kwargs=kwargs, args=(volume,), parse=False,
                    fail_ok=fail_ok)


def volume_list(client, parse=True, fail_ok=False, **kwargs):
    valid_flags = ('group_id', 'all_tenants', 'name', 'status', 'bootable',
                   'migration_status', 'metadata', 'image_metadata', 'marker',
                   'limit', 'fields', 'sort', 'tenant', 'filters',
                   'with_count')
    return _execute(client, cmd='list', valid_flags=valid_flags, kwargs=kwargs,
                    args=(), parse=parse, fail_ok=fail_ok)


def volume_show(client, volume, parse=True, fail_ok=False):
    return _execute(client, cmd='show', valid_flags=None, kwargs=None,
                    args=(volume,), parse=parse, fail_ok=fail_ok)


def snapshot_create(client, volume, parse=True, fail_ok=False, **kwargs):
    valid_flags = ('force', 'name', 'description', 'metadata')
    return _execute(client, cmd='snapshot-create', valid_flags=valid_flags,
                    kwargs=kwargs, args=(volume,), parse=parse,
                    fail_ok=fail_ok)


def snapshot_delete(client, snapshot, parse=True, fail_ok=False, **kwargs):
    return _execute(client, cmd='snapshot-delete', valid_flags=('force'),
                    kwargs=kwargs, args=(snapshot,), parse=parse,
                    fail_ok=fail_ok)


def snapshot_list(client, parse=True, fail_ok=False, **kwargs):
    valid_flags = ('all_tenants', 'name', 'status', 'volume_id', 'marker',
                   'limit', 'sort', 'tenant', 'metadata', 'filters',
                   'with_count')
    return _execute(client, cmd='snapshot-list', valid_flags=valid_flags,
                    kwargs=kwargs, args=(), parse=parse, fail_ok=fail_ok)


def snapshot_show(client, snapshot, parse=True, fail_ok=False):
    return _execute(client, cmd='snapshot-show', valid_flags=None, kwargs=None,
                    args=(snapshot,), parse=parse, fail_ok=fail_ok)

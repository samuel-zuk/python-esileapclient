import json
import esileapclient.tests.functional.utils.output_utils as utils


def _execute(client, cmd, valid_flags, kwargs, args, parse, fail_ok):
    flag_str = utils.kwargs_to_flags(valid_flags, kwargs) if kwargs else ''
    arg_str = '' if not len(args) else ' '.join(args)
    if parse:
        flag_str = ' '.join((flag_str, '-f json'))
        output = client.esi(cmd, flag_str, arg_str, fail_ok)
        return json.loads(output)
    else:
        return client.esi(cmd, flag_str, arg_str, fail_ok)


def offer_create(client, node_uuid, parse=True, fail_ok=False, **kwargs):
    valid_flags = ('resource_type', 'start_time', 'end_time',
                   'lessee', 'name', 'properties')
    return _execute(client, cmd='offer create', valid_flags=valid_flags,
                    kwargs=kwargs, args=(node_uuid,), parse=parse,
                    fail_ok=fail_ok)


def offer_delete(client, offer_uuid, fail_ok=False):
    return client.esi('offer delete', '', offer_uuid, fail_ok)


def offer_list(client, parse=True, fail_ok=False, **kwargs):
    valid_flags = ('long', 'status', 'project', 'resource_uuid',
                   'resource_type', 'time_range', 'availability_range')
    return _execute(client, cmd='offer list', valid_flags=valid_flags,
                    kwargs=kwargs, args=(), parse=parse, fail_ok=fail_ok)


def offer_show(client, offer_uuid, parse=True, fail_ok=False):
    return _execute(client, cmd='offer show', valid_flags=None, kwargs=None,
                    args=(offer_uuid,), parse=parse, fail_ok=fail_ok)


def offer_claim(client, offer_uuid, parse=True, fail_ok=False, **kwargs):
    valid_flags = ('start_time', 'end_time', 'properties')
    return _execute(client, cmd='offer claim', valid_flags=valid_flags,
                    kwargs=kwargs, args=(offer_uuid,), parse=parse,
                    fail_ok=fail_ok)


def lease_create(client, node_uuid, lessee, parse=True, fail_ok=False,
                 **kwargs):
    valid_flags = ('resource_type', 'start_time', 'end_time',
                   'name', 'properties')
    return _execute(client, cmd='lease create', valid_flags=valid_flags,
                    kwargs=kwargs, args=(node_uuid, lessee), parse=parse,
                    fail_ok=fail_ok)


def lease_list(client, parse=True, fail_ok=False, **kwargs):
    valid_flags = ('long', 'all', 'status', 'offer_uuid', 'time_range',
                   'project', 'owner', 'resource_type', 'resource_uuid')
    return _execute(client, cmd='lease list', valid_flags=valid_flags,
                    kwargs=kwargs, args=(), parse=parse, fail_ok=fail_ok)


def lease_delete(client, lease_uuid, fail_ok=False):
    return client.esi('lease delete', '', lease_uuid, fail_ok)


def lease_show(client, lease_uuid, parse=True, fail_ok=False):
    return _execute(client, cmd='lease show', valid_flags=None, kwargs=None,
                    args=(lease_uuid,), parse=parse, fail_ok=fail_ok)

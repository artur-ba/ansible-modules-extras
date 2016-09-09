#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

try:
    from monascaclient import client as monasca_client
    HAS_CLIENT = True
except ImportError:
    HAS_CLIENT = False

try:
    import shade
    HAS_SHADE = True
except ImportError:
    HAS_SHADE = False

DOCUMENTATION = '''
module: monasca_alarm_notification
short_description: Create a notification in monasca
description:
    - Creates a notification in monasca
version_added: "2.1.0.0"
author: "Artur Basiak (@artur-ba)"
requirements:
    - python-monascaclient
options:
    name:
        description:
            - Name of the notification
        required: true
    type:
        description:
            - Type of the notification, one of [EMAIL, WEBHOOK, PAGERDUTY]
        required: true
        default: EMAIL
        choices: [EMAIL, WEBHOOK, PAGERDUTY]
    address:
        description:
            - Address where notification should be sent
        required: true
        default: ''
    period:
        description:
            - How frequently a notification should be resent (only valid for
              webhook urls)
        required: true
        default: 0
    state:
        description:
            - One of the values [present, absent] is permitted
        required: false
        default: present
        choices: [present, absent]
'''

EXAMPLES = '''
Create a simple alarm notification:
- monasca_alarm_notification:
    name: Test
    type: EMAIL
    address: root@localhost
    period: 0
'''

def _handle_present(module, client, params):
    pass

def _handle_absent(module, client, params):
    pass

def _get_monasca_client():
    cloud = shade.operator_cloud(cloud='monasca')

    token = cloud.auth_token
    endpoint = cloud.get_endpoint(id='monasca',
                                  filters={'interface': 'public'})

    if not endpoint:
        raise Exception('Monasca API url is missing')
    client = monasca_client.Client('v2.0', endpoint, {
        token: token
    })

    return client

_TYPES = ('EMAIL', 'WEBHOOK', 'PAGERDUTY')
_STATES = {
    'present': _handle_present,
    'absent': _handle_absent
}

def main():
    argument_spec = openstack_full_argument_spec(
        name=dict(
            required=True,
            type='str'
        ),
        type=dict(
            required=True,
            type='str',
            default=_TYPES[0],
            choices=list(_TYPES)
        ),
        address=dict(
            required=True,
            type='str',
            default=''
        ),
        period=dict(
            required=True,
            type='int',
            default=0
        ),
        state=dict(
            required=False,
            type='str',
            default=_STATES.keys()[0],
            choices=list(_STATES.keys())
        )
    )

    module_kwargs = openstack_module_kwargs()
    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
        **module_kwargs
    )

    if not HAS_CLIENT:
        module.fail_json(msg='python-monascaclient is required for this module')
    if not HAS_SHADE:
        module.fail_json(msg='shade is required for this module')

    try:
        client = _get_monasca_client()
        state = module.params['state']
        _STATES[state](module, client, module.params)
    except Exception as ex:
        module.fail_json(msg=ex.message)

    module.exit_json('')

from ansible.module_utils.basic import *
from ansible.module_utils.openstack import *

if __name__ == "__main__":
    main()
#!/bin/python3
#
#   Copyright Red Hat, Inc. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#
# -*- coding: utf-8 -*-

import os
from texttable import Texttable
import yaml

# featureset mapping to match fs configuration files
# <feature_setting_name>: [<enabled_value>, <acronym>, <description>]
features_map = {
    'overcloud_ipv6': ['true', 'IPv6', 'Overcloud IPv6'],
    'ssl_overcloud': ['true', 'SSLoc', 'Overcloud SSL'],
    'network_isolation': ['true', 'NIsol', 'Network Isolation'],
    'network_isolation_type': ['single-nic-vlans|multiple-nics|bond',
                               'NItyp', 'Network Isolation Type'],
    'step_introspect': ['true', 'Intro', 'Introspection'],
    'undercloud_check_idempotency': ['true', 'Idemp',
                                     'Undercloud Idempotency Check'],
    'containerized_undercloud': ['true', 'ConUC', 'Containerized undecloud'],
    'containerized_overcloud': ['true', 'ConOC', 'Containerized overcloud'],
    'undercloud_upgrade': ['true', 'UPGuc', 'Undercloud Upgrade'],
    'containerized_overcloud_upgrade': ['true', 'UPGoc',
                                        'Overcloud Major Upgrade'],
    'overcloud_update': ['true', 'UPDoc', 'Overcloud Update (Minor Upgrade)'],
    'ffu_overcloud_upgrade': ['true', 'UPGff',
                              'Fast-forward Overcloud Upgrade'],
    'standalone_role': ['Standalone.yaml', 'Stdln', 'Standalone Deploy'],
    'run_tripleo_validations': ['true', 'Valid', 'Validations'],
    'test_ping': ['true', 'PingT', 'Ping and ssh tests'],
    'run_tempest': ['true', 'Temps', 'run Tempest'],
    'composable_scenario': ['', 'Scen#', 'Scenario ###'],
    'extra_args': ['ceph', 'Cephd', 'Ceph deploy'],
    'undercloud_heat_convergence': ['true', 'HConv',
                                    'Undercloud Heat Convergence'],
    'enable_minimal_browbeat': ['true', 'BrowB',
                                'Browbeat performance testing'],
    'validate_ha_overcloud': ['true', 'HAval', 'HA Validation'],
}

symbol_map = {
    'single-nic-vlans': [u'─', 'Network isolation single network interface'
                               ' card'],
    'multiple-nics': [u'☰', 'Network isolation multiple network interface'
                            'cards'],
    'release': [u'◍', 'Feature enabled in certain releases only'],
    'enabled': [u'◉', 'Feature enabled in all releases'],
    'disabled': [u'❍', 'Feature explicitly disabled in all releases'],
    'not-found': [u' ', 'Feature not found'],
}


def load_fs():
    t = Texttable()
    # headers/columns
    columns = ['Fset#']
    for k, h in sorted(features_map.items(), key=lambda kv: kv[1][1]):
        columns.append(h[1])

    matrix_length = len(columns)
    t.set_cols_width([5] * matrix_length)
    t.set_cols_align(['c'] * matrix_length)
    t.set_cols_valign(['m'] * matrix_length)
    t.set_cols_dtype(['t'] * matrix_length)

    root_path = os.path.dirname(os.path.realpath(__file__))
    fs_dir = os.path.join(root_path, 'config/general_config/')

    for fs_filename in sorted(os.listdir(fs_dir)):
        fs_dict = {}
        if fs_filename.startswith('featureset0') and \
           fs_filename.endswith('.yml'):
            with open(os.path.join(fs_dir, fs_filename)) as fs_file:
                fs_dict = yaml.load(fs_file, yaml.SafeLoader)
                datarow = get_data_from_yaml(fs_dict, fs_filename)
                t.add_rows([columns, datarow])
                fs_list.append(fs_filename[10:13])
    print(t.draw())
    print('\n')


def get_data_from_yaml(fs_dict, fs_filename):
    """Get data from fs yaml file

    :param ds_dict: featureset dictonary read from yaml file
    :param fs_filename: featureset yaml config file
    :returns list -- list of features read from yaml file
    """
    # Add XXX_ link to first column e.g. 001_
    datarow = [fs_filename[10:13] + '_']
    for k, v in sorted(features_map.items(), key=lambda kv: kv[1][1]):
        if k in fs_dict:
            # value = what the fs file has
            value = str.lower(str(fs_dict[k]))
            # enabled = what it should have to be active
            enabled = str.lower(str(v[0]))

            # get digits only from scenarioXXX in composable_scenario setting
            if k == 'composable_scenario':
                datarow.append(''.join([n for n in value if n.isdigit()]))
            # expects substr in extra_args e.g. 'ceph'
            elif k == 'extra_args' and enabled in value:
                datarow.append(symbol_map['enabled'][0])
            # fields that expects exact value e.g. 'true'
            elif value == enabled:
                datarow.append(symbol_map['enabled'][0])
            # expects a substr, transform it into a symbol
            elif value in enabled and value in symbol_map:
                datarow.append(symbol_map[value][0])
            # enabled in certain releases
            elif value.startswith('{%') and 'release' in value:
                datarow.append(symbol_map['release'][0])
            else:
                # feature is present but disabled e.g. 'false'
                datarow.append(symbol_map['disabled'][0])
        # feature not found in fs file
        else:
            datarow.append(symbol_map['not-found'][0])
    return datarow


def acronyms_and_symbols():
    at = Texttable()
    columns = ['Acronym', 'Definition']
    for k, acr in sorted(features_map.items(), key=lambda kv: kv[1][1]):
        at.add_rows([columns, [acr[1], acr[2]]])
    print(at.draw())
    print('\n')

    st = Texttable()
    columns = ['Symbol', 'Description']
    for k, symdef in sorted(symbol_map.items(), key=lambda kv: kv[1][1]):
        st.add_rows([columns, [symdef[0], symdef[1]]])
    print(st.draw())
    print('\n')

    baseurl = 'https://opendev.org/openstack/tripleo-quickstart'
    path = 'config/general_config/src/branch/master'
    for f in fs_list:
        print(".. _{0}: {1}/{2}/featureset{0}.yml".format(f, baseurl, path))


###

if __name__ == '__main__':
    fs_list = []
    load_fs()
    acronyms_and_symbols()
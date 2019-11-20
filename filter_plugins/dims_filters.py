# vim: set ts=4 sw=4 tw=0 et :

import bcrypt
import six
import socket

from netaddr import *
from ansible import errors

# Python3 has no basestring (use str instead)
basestring = str

def _list_to_string_args(_list):
    '''
    Return a comma separated list of strings.

    a = ['172.17.8.101', '172.17.8.102', '172.17.8.103']
    _list_to_string_args(a)
    '"172.17.8.101", "172.17.8.102", "172.17.8.103"'

    '''

    if type(_list) == type([]):
        return ", ".join(["\"{0}\"".format(i) for i in _list])
    else:
        return "{}".format(_list)

def _add_domain(_list, category='devops', deployment='local'):
    '''
    Return an array of names with added domains (for instances
    where fully qualified domain names are required.)

    a = ['node01','node02','node03']
    _add_domain(a, category='devops', deployment='local')
    ['node01.devops.local', 'node02.devops.local', 'node03.devops.local']

    '''

    if type(_list) == type([]):
        return ['{0}.{1}.{2}'.format(
                    host,
                    category,
                    deployment
                ) for host in _list]
    else:
        raise errors.AnsibleFilterError('Unrecognized input arguments to _add_domains()')


def _initial_cluster_lookup_short(_list, category='devops', deployment='local', port=2380):
    '''
    Return a comma (no spaces!) separated list of Consul initial cluster
    members. The "no spaces" is because this is used as a single command line
    argument.

    This filter only works if DNS resolution is available. To prevent templating
    errors, such a failure returns a null string. Calling programs can and should
    check for this error before attempting to use the results.

    a = ['node01','node02','node03']
    _initial_cluster_lookup_short(a)
    'node01=http://192.168.56.21:2380,node02=http://192.168.56.22:2380,node03=http://192.168.56.23:2380'

    $ ansible -i inventory/ -m debug -a msg="{{ groups.consul|initial_cluster() }}" node01.devops.local
    node01.devops.local | SUCCESS => {
      "changed": false,
      "msg": "node03=http://node03.devops.local:2380,node02=http://node02.devops.local:2380,node01=http://node01.devops.local:2380"
    }

    '''

    if type(_list) == type([]):
        try:
            return ','.join(
                ['{0}=http://{1}:{2}'.format(
                    i.decode('utf-8'),
                    socket.gethostbyname('{0}.{1}.{2}'.format(
                        i.decode('utf-8'),
                        category,
                        deployment)
                    ),
                    port) for i in _list]
            )
        except Exception as e:
            #raise errors.AnsibleFilterError(
            #    'initial_cluster() could not perform lookups: {0}'.format(str(e))
            #)
            return ''
    else:
        raise errors.AnsibleFilterError('Unrecognized input arguments to initial_cluster()')

def _initial_cluster(_list, port=2380):
    '''
    Return a comma (no spaces!) separated list of Consul initial cluster
    members from fully qualified domain names (e.g., Ansible group member
    names). The "no spaces" is because this is used as a single command line
    argument.

    a = ['node01.devops.local','node02.devops.local','node03.devops.local']
    _initial_cluster(a)
    'node01=http://node01.devops.local:2380,node02=http://node02.devops.local:2380,node03=http://node03.devops.local:2380'

    '''

    if type(_list) == type([]):
        try:
            return ','.join(
                ['{0}=http://{1}:{2}'.format(
                    i.decode('utf-8').split('.')[0],
                    i.decode('utf-8'),
                    port) for i in _list]
            )
        except Exception as e:
            #raise errors.AnsibleFilterError(
            #    'initial_cluster() filed to convert: {0}'.format(str(e))
            #)
            return ''
    else:
        raise errors.AnsibleFilterError('Unrecognized input arguments to initial_cluster()')


def _names_to_ips(_list, category='devops', deployment='local'):
    '''
    Return an array of IP addresses resulting from lookups of names
    in the input array. This function assumes the input array consists
    of short hostnames and will convert them into fully qualified domain
    names to perform lookups.

    a = ['node01','node02','node03']
    _names_to_ips(a)
    ['192.168.56.21', '192.168.56.22', '192.168.56.23']

    '''

    if type(_list) == type([]):
        try:
            return ['{0}'.format(
                    socket.gethostbyname('{0}.{1}.{2}'.format(
                        i.decode('utf-8'),
                        category,
                        deployment)))
                    for i in _list]
        except Exception as e:
            #raise errors.AnsibleFilterError(
            #    '_names_to_ips() could not perform lookups: {0}'.format(str(e))
            #)
            return ''
    else:
        raise errors.AnsibleFilterError('Unrecognized input arguments to _names_to_ips()')


def _ip_to_in_addr_arpa(_str):
    '''Return the reverse lookup address for an IP address'''

    if isinstance(_str, basestring):
        return IPAddress(_str).reverse_dns.split('.', 1)[-1][:-1]
    else:
        return "{}".format(_str)


def _bcrypt_hashpw(_str):
    '''Return the salted bcrypt hash of a password string'''
    # TODO(dittrich): Jenkins 2.89.2 dies with incompatible salt error when using default bcrypt salt prefix ("2y")
    # java.lang.IllegalArgumentException: Invalid salt revision
    #   at org.mindrot.jbcrypt.BCrypt.hashpw(BCrypt.java:757)
    #   at org.mindrot.jbcrypt.BCrypt.checkpw(BCrypt.java:856)
    #   at hudson.security.HudsonPrivateSecurityRealm$3.isPasswordValid(HudsonPrivateSecurityRealm.java:695)
    #   at hudson.security.HudsonPrivateSecurityRealm$4.isPasswordValid(HudsonPrivateSecurityRealm.java:716)
    #   at hudson.security.HudsonPrivateSecurityRealm$Details.isPasswordCorrect(HudsonPrivateSecurityRealm.java:522)
    #   ...
    #   See:  https://stackoverflow.com/questions/16478604/bcrypt-checkpw-invalid-salt-version-exception
    #   Until this is fixed, falling back to supported prefix "2a".

    if isinstance(_str, six.text_type):
        return "#jbcrypt:{}".format(bcrypt.hashpw(_str.encode("utf-8"), bcrypt.gensalt(prefix=b"2a")))
    else:
        return "#jbcrypt:{}".format(bcrypt.hashpw(_str, bcrypt.gensalt(prefix=b"2a")))


class FilterModule(object):
    '''DIMS Ansible filters.'''

    def filters(self):
        return {
            # List filters
            'list_to_string_args': _list_to_string_args,

            # Docker/Consul/Swarm filters
            'names_to_ips': _names_to_ips,
            'initial_cluster': _initial_cluster,
            'initial_cluster_lookup_short': _initial_cluster_lookup_short,
            'add_domain': _add_domain,

            # Networking filters
            'ip_to_in_addr_arpa': _ip_to_in_addr_arpa,

            # String filters
            'bcrypt_hashpw': _bcrypt_hashpw,

            # Other filters go here...
        }

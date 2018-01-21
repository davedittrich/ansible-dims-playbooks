# vim: set ts=4 sw=4 tw=0 et :
#
# Copyright (C) 2018, David Dittrich. All rights reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
# This lookup extracts the TXT record field from an opendkim .txt file.
#
# "201801._domainkey\tIN\tTXT\t( \"v=DKIM1; h=sha256; k=rsa; s=email; \"\n\t  \"p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEApZRpNnjWsbqldIIFFJQ+8VEgO4EVVbTFL7fmYB/BAOGdbNeCYyDNcM7b/
# 1SVjucrrWJgrUvYlQhydI1i33BN4veLgLjUE5WJg5FIT2d0wk1wawQ0g/rXgUTmhz2ouWSSE9DFsHGPmR7Pi+6w3BNJU12Xtd7RiXw4g567g/uniQ2TrMkFfxtVSwOJ6bPNvNBxVzPJN7pRVh3kdV\"\n\t  \"UFnnUY9BuC7O6debIOi3+QKdjocpCcLVXpHnJnKihTgp04JnvTYctxlVpWC8vr1D0JNgWlmjIWjr5KtrzG4fSVT5ZKFplLFHYI4jXCgbaQgxWO9d0IHSmPAfvObVKC0STNQx3AMQIDAQAB\" )  ; ----- DKIM key 201801 for secretsmgmt.tk"
#
# $ ansible -m debug -a "msg={{ lookup('dkim_txt_record', '/path/to/keys/domain_name/selector.txt') }}" host
#host | SUCCESS => {
#             "msg": "v=DKIM1; h=sha256; k=rsa; s=email; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEApZRpNnjWsbqldIIFFJQ+8VEgO4EVVbTFL7fmYB/BAOGdbNeCYyDNcM7b/1SVjucrrWJgrUvYlQhydI1i33BN4veLgLjUE5WJg5FIT2d0wk1wawQ0g/rXgUTmhz2ouWSSE9DFsHGPmR7Pi+6w3BNJU12Xtd7RiXw4g567g/uniQ2TrMkFfxtVSwOJ6bPNvNBxVzPJN7pRVh3kdVUFnnUY9BuC7O6debIOi3+QKdjocpCcLVXpHnJnKihTgp04JnvTYctxlVpWC8vr1D0JNgWlmjIWjr5KtrzG4fSVT5ZKFplLFHYI4jXCgbaQgxWO9d0IHSmPAfvObVKC0STNQx3AMQIDAQAB"

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import re

from ansible.plugins.lookup import LookupBase

class LookupModule(LookupBase):

    def run(self, args, variables=None, **kwargs):

        key_regex = re.compile(r'h=rsa-')
        split_regex = re.compile(r'"\t  "')
        txt_regex = re.compile(r'\( (?P<txt>.*) \)',
                re.MULTILINE)
        results = []
        txtstr = ""

        try:
            with open(args[0], 'r') as _file:
                txtstr = "".join([ _line.rstrip('\n') for _line in _file ])
        except IOError as e:
            txtstr = ""
        except Exception as e:
            raise e

        # Clean up string before parsing out TXT record content
        txtstr = key_regex.sub('h=', txtstr)
        txtstr = split_regex.sub('', txtstr)

        try:
            # Strip off the first/last characters (i.e., the " characters)
            results.append(txt_regex.search(txtstr).group('txt')[1:-1])
        except AttributeError as e:
            pass
        except Exception as e:
            raise e

        return results

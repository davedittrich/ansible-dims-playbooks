export OS=$(uname -s)
export PYTHONPATH=$(pwd)
export D2="python3 -m d2.main --debug"

load 'libs/bats-support/load'
load 'libs/bats-assert/load'


# vim: set ts=4 sw=4 tw=0 et :

load test_helper

# See definition of D2 in test_helpers.bash for why "main" is used
# in tests.

setup() {
    true
}

teardown() {
    true
}

@test "'d2 about' contains 'version'" {
    run bash -c "$D2 -q about"
    assert_output --partial 'version'
}

# vim: set ts=4 sw=4 tw=0 et :

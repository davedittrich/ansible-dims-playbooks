load test_helper

# See definition of D2 in test_helpers.bash for why "main" is used
# in tests.

setup() {
    true
}

teardown() {
    true
}

@test "'d2 help' can load all entry points" {
    run $D2 help 2>&1
    refute_output --partial "Could not load EntryPoint"
}

@test "'d2 --version' works" {
    run $D2 --version
    assert_output --partial "main"
}

# vim: set ts=4 sw=4 tw=0 et :

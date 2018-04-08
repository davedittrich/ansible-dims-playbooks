#!/usr/bin/env bats

@test "/VERSION exists and is not empty" {
  [ -s /VERSION ]
}

@test "/AUTHOR exists and is not empty" {
  [ -s /AUTHOR ]
}

@test "/LAST_UPDATED exists and is not empty" {
  [ -s /LAST_UPDATED ]
}



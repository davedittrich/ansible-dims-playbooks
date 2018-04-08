#!/bin/bash

DIR=/docker-entrypoint.d

if [[ "$VERBOSE" == "true" ]]
then
	ARGS+=" --verbose"
fi

# IMAGE and AUTHOR are set in Dockerfile at build time.

if [[ "$1" == "--help" ]]
then
	echo "${IMAGE:-unknown_image}: v$VERSION (author ${AUTHOR:-not specified})"
	cat $DIR/usage.txt
	exit 0
fi

if [[ -d $DIR ]]
then
  /bin/run-parts $ARGS --regex '\.sh$' "$DIR"
fi

exec "$@"

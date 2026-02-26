#!/bin/sh

set -eu

cd "$(dirname "$(readlink -f "$0")")"

is_failed=0

while IFS=: read -r name cmd; do
    printf '%-12s' "$name..."
    if $cmd >/dev/null 2>&1; then
	echo OK
    else
	is_failed=1
	echo "FAIL (cmd was: $cmd)"
    fi
done <<EOF
mypy:mypy .
tests.py:python -m unittest tests
flake8:flake8 .
isort:isort -c .
EOF

exit $is_failed

#!/usr/bin/env bash
#
# Test Python
#
# Example Call:
#    ./test_python_package.sh
#

echo "$(date +%c): Running Unit Tests"
pytest auto_recruiter indeed

TEST_STATUS=$?
echo "$(date +%c): Test Exit Status - ${TEST_STATUS}"

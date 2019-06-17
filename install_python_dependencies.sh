#!/usr/bin/env bash
#
# Install Python Dependencies For The Script
#

echo "$(date +%c): Installing Python Packages For auto_recruiter"
pip3 install -r auto_recruiter/requirements.txt

echo "$(date +%c): Installing Python Packages For Testing auto_recruiter"
pip3 install -r auto_recruiter/tests/requirements.txt

echo "$(date +%c): Installing Python Packages For the Indeed Class"
pip3 install -r indeed/requirements.txt

echo "$(date +%c): Installing Python Packages For Testing the Indeed Class"
pip3 install -r indeed/tests/requirements.txt


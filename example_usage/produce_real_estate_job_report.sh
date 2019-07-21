#!/usr/bin/env bash
#
# Prodcue "HR" Job Report
#
# Example: shell produce_hr_job_report.sh
#

echo "$(date +%c): Generating 'Human Resources' Job Report"
python3.6 ../auto_recruiter/generate_job_report.py --report-output-filename="hr_jobs" \
--report-output-dir="../data/job_reports" --min-jobs=200 --job-boards="indeed" \
--job-title="Human Resources"

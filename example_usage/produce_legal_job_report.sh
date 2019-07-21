#!/usr/bin/env bash
#
# Prodcue "Legal" Job Report
#
# Example: shell produce_legal_job_report.sh
#

echo "$(date +%c): Generating 'Legal' Job Report"
python3.6 ../auto_recruiter/generate_job_report.py --report-output-filename="hr_jobs" \
--report-output-dir="../data/job_reports" --min-jobs=200 --job-boards="indeed" \
--job-title="Legal Secretary" --job-title="Legal Administrative Assistant"

#!/usr/bin/env bash
#
# Prodcue "Insurance" Job Report
#
# Example: shell produce_insurance_job_report.sh
#

echo "$(date +%c): Generating 'Insurance' Job Report"
python3.6 ../auto_recruiter/generate_job_report.py --report-output-filename="insurance_jobs" \
--report-output-dir="../data/job_reports" --min-jobs=200 --job-boards="indeed" \
--job-boards="monster" --job-title="Insurance Claims"\
 --job-title="Insurance Customer Service" --job-title="Insurance Sales" \
 --job-title="Insurance Clerk" --job-title="Insurance Underwriting"

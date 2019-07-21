#!/usr/bin/env bash
#
# Prodcue "Finance" Job Report
#
# Example: shell produce_finance_job_report.sh
#

echo "$(date +%c): Generating 'Finance' Job Report"
python3.6 ../auto_recruiter/generate_job_report.py --report-output-filename="finance_jobs" \
--report-output-dir="../data/job_reports" --min-jobs=200 --job-boards="indeed" \
--job-title="Accounts Receivable" --job-title="Billing Administrator" \
--job-title="Accounts Payable" --job-title="Payroll Specialist"

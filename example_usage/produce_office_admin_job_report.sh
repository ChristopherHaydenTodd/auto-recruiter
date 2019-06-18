#!/usr/bin/env bash
#
# Prodcue "Office Admin" Job Report
#
# Example: shell produce_office_admin_job_report.sh
#

echo "$(date +%c): Generating 'Office Administrator' Job Report"
python3.6 ../auto_recruiter/generate_job_report.py --report-output-filename="office_admin_jobs" \
--report-output-dir="../data/job_reports" --min-jobs=200 --job-boards="indeed" \
--job-boards="monster" --job-title="Administrative Assistant"\
 --job-title="Office Administrator" --job-title="Office Assistant" \
 --job-title="Meeting Coordinator"

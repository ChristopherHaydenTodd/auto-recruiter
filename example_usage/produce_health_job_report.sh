#!/usr/bin/env bash
#
# Prodcue "Health" Job Report
#
# Example: shell produce_health_job_report.sh
#

echo "$(date +%c): Generating 'Health' Job Report"
python3.6 ../auto_recruiter/generate_job_report.py --report-output-filename="health_jobs" \
--report-output-dir="../data/job_reports" --min-jobs=200 --job-boards="indeed" \
--job-title="Patient Services Associate" --job-title="Benefits Representative" \
--job-title="Health Admissions Coordinator"

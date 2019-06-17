# Project for Automating Searching for a Job

The auto-recruiter project is used for simplifying the process of looking for a job. The codebase has been set to pull and parse jobs from Indeed, Monster (TBD), and Career Builder (TBD).

## Table of Contents

- [Dependencies](#dependencies)
- [Executables](#executables)
- [Notes](#notes)
- [TODO](#todo)

## Dependencies

### Python Packages

 - beautifulsoup4>=4.7.1
 - ctodd-python-lib-data-structures>=1.0.0
 - ctodd-python-lib-execution>=1.0.0
 - ctodd-python-lib-logging>=1.0.0
 - pytz>=2019.1
 - XlsxWriter>=1.1.8

## Executables

### [generate_job_report.py](https://github.com/ChristopherHaydenTodd/auto-recruiter/blob/master/auto_recruiter/generate_job_report.py)

```
    Purpose:
        Script responsible for pulling jobs from job boards and generating a
        report. for each job title and job board
    Steps:
        - Parse CLI args
        - For each job board and job title
            - pull job listings based on the search params
            - pull details for each job in the list
        - Generate a report with all of the jobs

    usage:
        python3.6 generate_job_report.py
            --job-boards {indeed,monster,career_builder} -
            -job-titles JOB_TITLES
            [--report-output-filename REPORT_OUTPUT_FILENAME]
            [--report-output-dir REPORT_OUTPUT_DIR]
            [--min-jobs MIN_JOBS_TO_FIND]
            [--zip-code ZIP_CODE] [--radius RADIUS]
            [--job-type {fulltime,parttime,contractor}]
            [--salary-min SALARY_MIN]

    example call:
        python3.6 auto_recruiter/generate_job_report.py \
            --report-output-filename="office_admin_jobs" \
            --report-output-dir="../data/job_reports" --min-jobs=15 \
            --job-boards="indeed"  --job-boards="monster" \
            --job-title="Administrative Assistant"\
            --job-title="Office Administrator" --job-title="Office Assistant" \
            --job-title="Meeting Coordinator"
```

## Notes

 - Relies on f-string notation, which is limited to Python3.6.  A refactor to remove these could allow for development with Python3.0.x through 3.5.x

## TODO

 - Unittest framework in place, but lacking tests

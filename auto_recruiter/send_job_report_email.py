#!/usr/bin/env python3.6
"""
    Purpose:
        Send the job reports through email

    Steps:
        - Parse CLI to get who to send email to and what reports to send
        - Verify that email report exists
        - Set up and configure gmail server
        - Prepare email
        - Send email

    Usage:
        send_job_report_email.py
            [-h]
            [--gmail-token-file GMAIL_TOKEN_FILE]
            [--gmail-credentials-file GMAIL_CREDENTIALS_FILE]
            --gmail-account GMAIL_ACCOUNT
            --email-to EMAIL_TO
            --job-report-base-dir JOB_REPORT_BASE_DIR

    Example Call:


"""

# Python Library Imports
import logging
import os
import sys
from argparse import ArgumentParser
from datetime import datetime
from execution_helpers import function_executors
from logging_helpers import loggers
from os import listdir
from os.path import isfile, join

# Local Library Imports
from email_helpers import gmail_helpers


@function_executors.main_executor
def main():
    """
    Purpose:
        Read an .avro File
    """
    logging.info("Starting Job Report Email Process")

    cli_args = get_cli_arguments()

    job_report_files = get_available_job_reports(
        cli_args.job_report_base_dir
    )

    gmail_credentials = gmail_helpers.get_gmail_credentials(
        gmail_credentials_file=cli_args.gmail_credentials_file,
        gmail_token_file=cli_args.gmail_token_file,
    )
    gmail_service = gmail_helpers.get_gmail_service(gmail_credentials)

    report_email_message = build_report_email_message(
        cli_args.gmail_account, cli_args.email_to, job_report_files
    )

    gmail_helpers.send_email(gmail_service, report_email_message)

    logging.info("Job Report Email Process Complete")


###
# Get Reports to Send
###


def get_available_job_reports(job_report_base_dir, report_date=None):
    """
    Purpose:
        Get availale job reports to send
    Args:
        job_report_base_dir (String): Base dir to look for reports
    Returns:
        job_report_files (List of Strings): Available Reports to Send
    """

    if not report_date:
        report_date = datetime.now().strftime("%Y%m%d")

    job_report_files = [
        f"{job_report_base_dir}/{job_report}"
        for job_report
        in listdir(job_report_base_dir)
        if isfile(join(job_report_base_dir, job_report))
        and job_report.endswith(".xlsx")
        and report_date in job_report
    ]

    return job_report_files


###
# Report Email
###


def build_report_email_message(
    gmail_account,
    email_to,
    job_report_files,
    report_date=None
):
    """
    Purpose:
        Build Job Report email and attach all of the report files as attachements
    Args:
        gmail_account (String): Email address to use to send the email
        email_to (List of Strings): List of emails to send to
        job_report_files (List of Strings): Available Reports to Send
        report_date (String): Date to show in the report
    Returns:
        email_msg (Encoded Email Msg): Email Message ready to send
    """

    if not report_date:
        report_date = datetime.now().strftime("%b %d, %Y")

    email_msg = gmail_helpers.build_msg_obj(
        gmail_account,
        f"Job Report: {report_date}",
        "Attached are the jobs found from Indeed",
        email_to,
        email_attachments=job_report_files,
    )

    return email_msg

###
# General/Helper Methods
###


def get_cli_arguments():
    """
    Purpose:
        Parse CLI arguments for script
    Args:
        N/A
    Return:
        N/A
    """
    logging.info("Getting and Parsing CLI Arguments")

    parser = ArgumentParser(description="Send Test Email With Gmail")
    required = parser.add_argument_group('Required Arguments')
    optional = parser.add_argument_group('Optional Arguments')

    # Optional Arguments
    optional.add_argument(
        "--gmail-token-file",
        dest="gmail_token_file",
        help="Gmail Token Filename",
        required=False,
        type=str,
        default=os.path.expanduser("~/.gmail/gmail_token.pickle"),
    )
    optional.add_argument(
        "--gmail-credentials-file",
        dest="gmail_credentials_file",
        help="Gmail Credential Filename",
        required=False,
        type=str,
        default=os.path.expanduser("~/.gmail/gmail_credentials.json"),
    )


    # Required Arguments
    required.add_argument(
        "--gmail-account",
        dest="gmail_account",
        help="Gmail account to use to send email",
        required=True,
        type=str,
    )
    required.add_argument(
        "--email-to",
        dest="email_to",
        help="Emails to TO",
        required=True,
        action="append",
        type=str,
    )
    required.add_argument(
        "--job-report-base-dir",
        dest="job_report_base_dir",
        help="Base Dir to Check for Job Reports",
        required=True,
        type=str,
    )

    return parser.parse_args()


if __name__ == "__main__":

    try:
        loggers.get_stdout_logging(
            log_level=logging.INFO, log_prefix="[send_job_report_email] "
        )
        main()
    except Exception as err:
        print(
            "{0} failed due to error: {1}".format(os.path.basename(__file__), err)
        )
        raise err

#!/usr/bin/env python3.6
"""
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
"""

# Python Library Imports
import logging
import os
import pytz
import re
import shutil
import sys
import xlsxwriter
from argparse import ArgumentParser
from data_structure_helpers import string_helpers
from datetime import datetime
from execution_helpers import function_executors
from logging_helpers import loggers

# Local Library Imports
BASE_PROJECT_PATH = f"{os.path.dirname(os.path.realpath(__file__))}/../"
sys.path.insert(0, BASE_PROJECT_PATH)
from config import config
from indeed import indeed

# Globals
CONFIGS = config.Config.get()


###
# Main Execution
###


@function_executors.main_executor
def main():
    """
    Purpose:
        Get File Metadata
    """
    logging.info("Starting Process To Find Jobs For Me")

    cli_args = get_cli_arguments()

    job_board_functions = {
        "indeed": get_job_listings_from_indeed,
        "monster": get_job_listings_from_monster,
        "career_builder": get_job_listings_from_career_builder,
    }
    job_listings_by_job_board = {}

    for job_board in cli_args.job_boards:

        job_listings_by_title = {}
        for job_title in cli_args.job_titles:
            job_listings_by_title[job_title] =\
                job_board_functions[job_board](
                    job_title,
                    cli_args.zip_code,
                    cli_args.radius,
                    cli_args.job_type,
                    cli_args.salary_min,
                    cli_args.min_jobs_to_find,
                )

        job_listings_by_job_board[job_board] = job_listings_by_title

    create_job_report(
        cli_args.report_output_dir,
        cli_args.report_output_filename,
        job_listings_by_job_board
    )

    logging.info("Starting Process To Find Jobs For Me Complete")


###
# Job Listing Functions
###


def get_job_listings_from_indeed(
    job_title, zip_code, radius, job_type, salary_min, min_jobs_to_find
):
    """
    Purpose:
        Get Job Listings from Indeed by filtering on the cli args for
        job_title, zip_code, radius, job_type, and salary
    Args:
        job_title (String): job title to Search (keywords in Indeed)
        zip_code (String): Zip code to center the job search on
        radius (String): Radius (from the zip code center) that jobs need to be
            in to be considered
        job_type (String): type of job. Enum of the following:
            [fulltime, parttime, contractor]
        salary_min (String): Minimum salary for jobs to be returned (best guess if
            none is provided)
        min_jobs_to_find (String): How many jobs to attempt to find. will loop through
            calls to Indeed until this number is met or if 5 calls in a row yeild
            no new results
    Returns:
        job_listings (List of Dicts): A list of Dicts. Key is the job ID and the
            dict holds all of the job listing details.
    """

    job_listings = {}

    job_listing_pagination = 0
    pagination_non_increment_counter = 0
    while job_listing_pagination < min_jobs_to_find:
        logging.info(f"Finding Jobs ({job_listing_pagination} of {min_jobs_to_find})")

        new_job_listings = indeed.Indeed.get_job_listings(
            job_title,
            zip_code,
            radius=radius,
            job_type=job_type,
            salary_min=salary_min,
            pagination=job_listing_pagination,
        )

        for job_listing in new_job_listings:
            job_listings[job_listing["job_id"]] = job_listing

        if (
            job_listing_pagination == len(job_listings)
            and pagination_non_increment_counter < 5
        ):
            logging.info(
                "No Unqiue Jobs Found On Loop (This is loop "
                f"#{pagination_non_increment_counter}), Continuing"
            )
            pagination_non_increment_counter += 1
            continue
        elif (
            job_listing_pagination == len(job_listings)
            and pagination_non_increment_counter >= 5
        ):
            logging.info(
                "No Unqiue Jobs Found On Loop (This is loop "
                f"#{pagination_non_increment_counter}), Exiting"
            )
            break
        else:
            job_listing_pagination = len(job_listings)
            pagination_non_increment_counter = 0

    return job_listings


def get_job_listings_from_monster(
    job_title, zip_code, radius, job_type, salary_min, min_jobs_to_find
):
    """
    Purpose:
        Get Job Listings from Monster by filtering on the cli args for
        job_title, zip_code, radius, job_type, and salary
    Args:
        job_title (String): job title to Search (keywords in Monster)
        zip_code (String): Zip code to center the job search on
        radius (String): Radius (from the zip code center) that jobs need to be
            in to be considered
        job_type (String): type of job. Enum of the following:
            [fulltime, parttime, contractor]
        salary_min (String): Minimum salary for jobs to be returned (best guess if
            none is provided)
        min_jobs_to_find (String): How many jobs to attempt to find. will loop through
            calls to Monster until this number is met or if 5 calls in a row yeild
            no new results
    Returns:
        job_listings (List of Dicts): A list of Dicts. Key is the job ID and the
            dict holds all of the job listing details.
    """
    logging.warning("Monster Job Board Not Implemented Yet")

    job_listings = {}

    return job_listings


def get_job_listings_from_career_builder(
    job_title, zip_code, radius, job_type, salary_min, min_jobs_to_find
):
    """
    Purpose:
        Get Job Listings from Career Builder by filtering on the cli args for
        job_title, zip_code, radius, job_type, and salary
    Args:
        job_title (String): job title to Search (keywords in Career Builder)
        zip_code (String): Zip code to center the job search on
        radius (String): Radius (from the zip code center) that jobs need to be
            in to be considered
        job_type (String): type of job. Enum of the following:
            [fulltime, parttime, contractor]
        salary_min (String): Minimum salary for jobs to be returned (best guess if
            none is provided)
        min_jobs_to_find (String): How many jobs to attempt to find. will loop through
            calls to Career Builder until this number is met or if 5 calls in a row yeild
            no new results
    Returns:
        job_listings (List of Dicts): A list of Dicts. Key is the job ID and the
            dict holds all of the job listing details.
    """
    logging.warning("Career Builder Job Board Not Implemented Yet")

    job_listings_from_career_builder = {}

    return job_listings


def get_global_job_listings(job_listings_by_job_board):
    """
    Purpose:
        Flatten the job listings from all job_boards and job_titles into a single
        list of dictionaries. Add in a column for what job board the data was
        found and what the search was that yielded the job (will use the first
        title if a job shows up on multiple queries (boards wont matter as they
        will have unique ids and other thigns)
    Args:
        job_listings_by_job_board (List of Dicts): A list of Dicts. Key is the job ID
            and the dict holds all of the job listing details.
    Returns:
        global_job_listings (List of Dicts): A list of Dicts. Key is the job ID and the
            dict holds all of the job listing details.
    """

    global_job_listings = {}

    for job_board, job_listings_by_title in job_listings_by_job_board.items():
        for job_title, job_listings in job_listings_by_title.items():
            for job_id, job_listing in job_listings.items():
                global_job_listings[job_id] = job_listing
                global_job_listings[job_id]["job_board"] = job_board
                global_job_listings[job_id]["job_search"] = job_title

    return global_job_listings


###
# Report Generator
###


def create_job_report(
    report_output_dir, report_output_filename, job_listings_by_job_board
):
    """
    Purpose:
        Create the Job Report with the job listings provided
    Args:
        report_output_dir (String): Location to put the filename. Specifically, the
            base directory
        report_output_filename (String): Location to put the filename. Specifically, the
            base of the filename (will append date)
        job_listings_by_job_board (List of Dicts): A list of Dicts. Key is the job ID
            and the dict holds all of the job listing details.
    Returns:
        N/A
    """

    if not job_listings_by_job_board:
        logging.error("No Job Boards Found, Unable to Generate Report")
        return

    # Create a workbook and add a worksheet.
    report_date = datetime.now(pytz.timezone("US/Eastern")).strftime("%Y%m%d")
    workbook = xlsxwriter.Workbook(
        f"{report_output_dir}/{report_output_filename}_{report_date}.xlsx"
    )

    # Generate the Global Worksheet First
    global_job_listings = get_global_job_listings(job_listings_by_job_board)
    create_global_worksheet(workbook, "Global", global_job_listings)

    # Generate a Sheet for Each Job Board/Job Title Combination
    for job_board, job_listings_by_title in job_listings_by_job_board.items():
        for job_title, job_listings in job_listings_by_title.items():

            sheet_name = "{job_board} - {job_title}".format(
                job_board=string_helpers.convert_to_title_case(job_board),
                job_title=string_helpers.convert_to_title_case(job_title),
            )
            sheet_name = (
                (sheet_name[:28] + "..") if len(sheet_name) > 31 else sheet_name
            )

            create_job_board_worksheet(workbook, sheet_name, job_listings)

    workbook.close()


def create_job_board_worksheet(workbook, sheet_name, job_listings):
    """
    Purpose:
        Create a sheet in the job report for job listings of a specific job board and
        job title combination. (e.g. job listings for "Administrative Assistant" in
        Indeed)
    Args:
        workbook (XlsxWriter Workbook Object): The open workbook object to add the
            sheet to
        sheet_name (String): Name of the sheet to add to the workbook
        job_listings (List of Dicts): A list of Dicts. Key is the job ID
            and the dict holds all of the job listing details.
    Returns:
        N/A
    """

    if not job_listings:
        logging.error(f"No {sheet_name} Job Listings to Generate Report")
        return

    # Create Worksheet
    worksheet = workbook.add_worksheet(sheet_name)

    # Set Cell Format
    cell_format = workbook.add_format()
    cell_format.set_text_wrap()

    # Get Headers
    headers = get_headers_for_job_title_listing_worksheets()

    # Set Column Widths
    for header_idx, header in enumerate(headers):
        worksheet.set_column(f"{header['column']}:{header['column']}", header["width"])

    # Set Row Height
    min_row = 1
    max_row = 1 + len(job_listings)
    for row_idx in range(1, max_row):
        worksheet.set_row(row_idx, 32)

    # Set Table Options
    table_dimensions = "{column_start}{row_start}:{column_end}{row_end}".format(
        column_start="A",
        row_start=min_row,
        column_end=chr((ord("A") - 1) + len(headers)),
        row_end=max_row,
    )
    table_options = {
        "name": re.sub("[^a-zA-Z]+", "", sheet_name)
    }
    worksheet.add_table(table_dimensions, table_options)

    header_row_idx = 0
    for header_column_idx, header in enumerate(headers):
        worksheet.write(header_row_idx, header_column_idx, header["title"])

    job_listing_row_idx = 1
    for job_id, job_details in job_listings.items():

        for header_column_idx, header in enumerate(headers):
            worksheet.write(
                job_listing_row_idx,
                header_column_idx,
                job_details[header["name"]],
                cell_format,
            )

        job_listing_row_idx += 1


def create_global_worksheet(workbook, sheet_name, job_listings):
    """
    Purpose:
        Create a sheet in the job report with all of the job listings flattened and
        all duplicates removed
    Args:
        workbook (XlsxWriter Workbook Object): The open workbook object to add the
            sheet to
        sheet_name (String): Name of the sheet to add to the workbook
        job_listings (List of Dicts): A list of Dicts. Key is the job ID
            and the dict holds all of the job listing details.
    Returns:
        N/A
    """

    if not job_listings:
        logging.error(f"No {sheet_name} Job Listings to Generate Report")
        return

    # Create Worksheet
    worksheet = workbook.add_worksheet(sheet_name)

    # Set Cell Format
    cell_format = workbook.add_format()
    cell_format.set_text_wrap()

    # Get Headers
    headers = get_headers_for_global_job_listing_worksheets()

    # Set Column Widths
    for header_idx, header in enumerate(headers):
        worksheet.set_column(f"{header['column']}:{header['column']}", header["width"])

    # Set Row Height
    min_row = 1
    max_row = 1 + len(job_listings)
    for row_idx in range(1, max_row):
        worksheet.set_row(row_idx, 32)

    # Set Table Options and Create Table
    table_dimensions = "{column_start}{row_start}:{column_end}{row_end}".format(
        column_start="A",
        row_start=min_row,
        column_end=chr((ord("A") - 1) + len(headers)),
        row_end=max_row,
    )
    table_options = {
        "name": re.sub("[^a-zA-Z]+", "", sheet_name)
    }
    worksheet.add_table(table_dimensions, table_options)

    header_row_idx = 0
    for header_column_idx, header in enumerate(headers):
        worksheet.write(header_row_idx, header_column_idx, header["title"])

    job_listing_row_idx = 1
    for job_id, job_details in job_listings.items():

        for header_column_idx, header in enumerate(headers):
            worksheet.write(
                job_listing_row_idx,
                header_column_idx,
                job_details[header["name"]],
                cell_format,
            )

        job_listing_row_idx += 1


def get_headers_for_job_title_listing_worksheets():
    """
    Purpose:
        Get the headers and their Excel format for the each job listings sheet
    Args:
        N/A
    Returns:
        headers (List of Dicst): A list of Dicts holding headers and their
            Excel format for each job listings sheet
    """

    headers = [
        {
            "name": "company",
            "title": string_helpers.convert_to_title_case("company"),
            "width": 20,
        },
        {
            "name": "job_title",
            "title": string_helpers.convert_to_title_case("job_title"),
            "width": 30,
        },
        {
            "name": "job_summary",
            "title": string_helpers.convert_to_title_case("job_summary"),
            "width": 50,
        },
        {
            "name": "city",
            "title": string_helpers.convert_to_title_case("city"),
            "width": 25,
        },
        {
            "name": "state",
            "title": string_helpers.convert_to_title_case("state"),
            "width": 25,
        },
        {
            "name": "zip_code",
            "title": string_helpers.convert_to_title_case("zip_code"),
            "width": 15,
        },
        {
            "name": "date_posted",
            "title": string_helpers.convert_to_title_case("date_posted"),
            "width": 15,
        },
        {
            "name": "job_type",
            "title": string_helpers.convert_to_title_case("job_type"),
            "width": 25,
        },
        {
            "name": "job_id",
            "title": string_helpers.convert_to_title_case("job_id"),
            "width": 20,
        },
        {
            "name": "easy_apply",
            "title": string_helpers.convert_to_title_case("easy_apply"),
            "width": 15,
        },
        {
            "name": "job_url",
            "title": string_helpers.convert_to_title_case("job_url"),
            "width": 100,
        },
    ]

    # Set Column Naming
    for header_idx, header in enumerate(headers):
        header["column"] = chr(ord("A") + header_idx)

    return headers


def get_headers_for_global_job_listing_worksheets():
    """
    Purpose:
        Get the headers and their Excel format for the global job listings sheet
    Args:
        N/A
    Returns:
        global_headers (List of Dicst): A list of Dicts holding headers and their
            Excel format for the global job listings sheet
    """

    global_headers = get_headers_for_job_title_listing_worksheets()
    global_headers.insert(
        0,
        {
            "name": "job_board",
            "title": string_helpers.convert_to_title_case("job_board"),
            "width": 20,
        },
    )
    global_headers.insert(
        1,
        {
            "name": "job_search",
            "title": string_helpers.convert_to_title_case("job_search"),
            "width": 20,
        },
    )

    # Set Column Naming
    for header_idx, header in enumerate(global_headers):
        header["column"] = chr(ord("A") + header_idx)

    return global_headers


###
# Scrpt Configuration Functions
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

    parser = ArgumentParser(description="Find Jobs from job boards online")
    required = parser.add_argument_group("Required Arguments")
    optional = parser.add_argument_group("Optional Arguments")

    # Required Arguments
    required.add_argument(
        "--job-boards",
        help="What job boards to search",
        dest="job_boards",
        action="append",
        type=str,
        default=[],
        choices=["indeed", "monster", "career_builder"],
        required=True,
    )
    required.add_argument(
        "--job-titles",
        help="What job titles to search",
        dest="job_titles",
        action="append",
        type=str,
        default=[],
        required=True,
    )

    # Optional Arguments
    optional.add_argument(
        "--report-output-filename",
        dest="report_output_filename",
        help="Base for the Report Output Filename (Only the base, Date will be added)",
        type=str,
        default="jobs",
        required=False,
    )
    optional.add_argument(
        "--report-output-dir",
        dest="report_output_dir",
        help="Base for the Report Output Directory",
        type=str,
        default=".",
        required=False,
    )
    optional.add_argument(
        "--min-jobs",
        dest="min_jobs_to_find",
        help="Min number of jobs to search for on indeed (May Return Less if board doesnt find more)",
        type=int,
        default=200,
        required=False,
    )
    optional.add_argument(
        "--zip-code",
        dest="zip_code",
        help="What Zip Code to Search",
        type=str,
        default="08096",
        required=False,
    )
    optional.add_argument(
        "--radius",
        dest="radius",
        help="What radius to search (Center is the zip code)",
        type=int,
        default=15,
        required=False,
    )
    optional.add_argument(
        "--job-type",
        dest="job_type",
        help="What Type of Job",
        type=str,
        default="fulltime",
        choices=["fulltime", "parttime", "contractor"],
        required=False,
    )
    optional.add_argument(
        "--salary-min",
        dest="salary_min",
        help="What is the base salary",
        type=str,
        default="$40,000",
        required=False,
    )

    return parser.parse_args()


if __name__ == "__main__":

    try:
        loggers.get_stdout_logging(
            log_level=logging.INFO, log_prefix="[generate_job_report] "
        )
        main()
    except Exception as err:
        logging.exception(f"{os.path.basename(__file__)} failed due to error: {err}")
        raise err
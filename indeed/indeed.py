#!/usr/bin/env python3
"""
    Purpose:
        The Indeed class is responsible for connecting to Indeed.com and using the tool
        to find jobs.
"""

# Python Library Imports
import json
import logging
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


###
# Class Definition
###


class Indeed(object):
    """
        Indeed Class. Handles requesting data from Indeed website and parsing the
        results into consumable components
    """

    ###
    # Properties
    ###

    expected_headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "accept-encoding": "gzip, deflate, sdch, br",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "referer": "https: //www.indeed.com/",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
    }

    ###
    # Class Lifecycle Methods
    ###

    def __init__(self):
        """
        Purpose:
            Initilize the Indeed Class.
        Args:
            N/A
        Returns:
            N/A
        """
        logging.info("Initializing Indeed")

    #####
    ## Get Functions
    #####

    @staticmethod
    def get_job_listings(
        keywords,
        zip_code,
        radius=15,
        job_type="fulltime",
        salary_min="$40,000",
        pagination=0
    ):
        """
        Purpose:
            Get Job Listings by keyword, zip_code, radius, job_type, and salary
        Args:
            keywords (String): Keywords to Search
            zip_code (String): Zip code to center the job search on
            radius (String): Radius (from the zip code center) that jobs need to be
                in to be considered
            job_type (String): type of job. Enum of the following:
                [fulltime, parttime, contractor]
            salary_min (String): Minimum salary for jobs to be returned (best guess if
                none is provided)
            pagination (String): The job to start on. If 0, page 1 of results. Page 2
                starts at 10. This gets different results depending on usage
        Returns:
            job_listings (List of Dicts): A list of Dicts. Key is the job ID and the
                dict holds all of the job listing details.
        """
        logging.info(f"Searching for jobs with keywords: {keywords}")

        job_listings = []

        raw_job_listing_html = Indeed.request_job_listings_from_indeed(
            keywords,
            zip_code,
            radius=radius,
            job_type=job_type,
            salary_min=salary_min,
            pagination=pagination,
        )

        # Parsing The Job HTML
        if raw_job_listing_html:
            job_listings = Indeed.parse_job_listings_html(raw_job_listing_html)
        else:
            logging.error(f"Failed to Fetch Job Listings from Indeed URL, exiting")

        # Get More Information For Each Job Listing
        for job_listing in job_listings:

            # Add Job Type As A Field
            if job_type == "fulltime":
                job_listing["job_type"] = "Full Time"
            elif job_type == "partime":
                job_listing["job_type"] = "Part Time"
            else:
                job_listing["job_type"] = "Unknown"

            # Get Job Details
            job_details = Indeed.get_job_details(
                job_listing["company"],
                job_listing["job_title"],
                job_listing["job_id"],
            )
            for job_detail, job_detail_value in job_details.items():
                job_listing[job_detail] = job_detail_value

        return sorted(job_listings, key = lambda i: i["company"])

    @staticmethod
    def get_job_details(company, job_title, job_id):
        """
        Purpose:
            Get Job Details
        Args:
            company (String): ...
            job_id (String): ...
            job_req (String): ...
        Returns:
            N/A
        """

        job_details = {}

        raw_job_details_html =\
            Indeed.request_job_details_from_indeed(company, job_title, job_id)

        # Parsing The Job HTML
        if raw_job_details_html:
            job_details = Indeed.parse_job_details_html(raw_job_details_html)
        else:
            logging.error(f"Failed to Fetch Job Details from Indeed URL, exiting")
            job_details["job_description"] = None
            job_details["job_apply_url"] = None
            job_details["job_posting_timeframe"] = None
            job_details["job_posting_datetime"] = None
            job_details["init_data"] = {}
            job_details["city"] = None
            job_details["state"] = None
            job_details["zip_code"] = None
            job_details["college_degree"] = None

        # Adding in the URL for easier searching =
        job_details["job_details_url"] =\
            Indeed.generate_job_details_url(company, job_title, job_id)

        return job_details

    ###
    # Functions to Pull Raw Results From to Indeed.com
    ###

    @staticmethod
    def request_job_listings_from_indeed(
        keywords,
        zip_code,
        radius=15,
        job_type="fulltime",
        salary_min="$40,000",
        pagination=0
    ):
        """
        Purpose:
            Get Job Listing HTML from Indeed.com by calling the website and
            parsing the results into a dict. Search for jobs using
            keyword, zip_code, radius, job_type, and salary
        Args:
            keywords (String): Keywords to Search
            zip_code (String): Zip code to center the job search on
            radius (String): Radius (from the zip code center) that jobs need to be
                in to be considered
            job_type (String): type of job. Enum of the following:
                [fulltime, parttime, contractor]
            salary_min (String): Minimum salary for jobs to be returned (best guess if
                none is provided)
            pagination (String): The job to start on. If 0, page 1 of results. Page 2
                starts at 10. This gets different results depending on usage
        Returns:
            raw_job_listing_html (String): Raw HTML results from Indeed.com of the job
                listings matching the search criteria
        """

        keywords = keywords.lower().replace(" ", "+")

        job_listing_url = (
            f"https://www.indeed.com/jobs?q={keywords}+{salary_min}&l="
            f"{zip_code}&radius={radius}&jt={job_type}&start={pagination}"
        )

        logging.info(f"Fetching HTML from Indeed URL: {job_listing_url}")
        job_listing_response = requests.get(
            job_listing_url, headers=Indeed.expected_headers
        )

        if job_listing_response.status_code == 200:
            raw_job_listing_html = job_listing_response.text
        else:
            logging.error(
                "Got Failure Response from Indeed.com: "
                f"{job_listing_response.status_code}"
            )
            raw_job_listing_html = None

        return raw_job_listing_html

    @staticmethod
    def request_job_details_from_indeed(company, job_title, job_id):
        """
        Purpose:
            Get Job Details HTML from Indeed.com by calling the website and
            parsing the results into a dict.
        Args:
            company (String): Name of the company the job is with
            job_title (String): The title of the position with the company
            job_id (String): The unqiue job_id from Indeed
        Returns:
            raw_job_details_html (String): Raw HTML results from Indeed.com of the job
                details
        """

        # Getting URL
        job_details_url = Indeed.generate_job_details_url(company, job_title, job_id)

        logging.info(f"Fetching HTML from Indeed URL: {job_details_url}")
        job_details_response = requests.get(
            job_details_url, headers=Indeed.expected_headers
        )

        if job_details_response.status_code == 200:
            raw_job_details_html = job_details_response.text
        else:
            logging.error(
                "Got Failure Response from Indeed.com: "
                f"{job_details_response.status_code}"
            )
            raw_job_details_html = None

        return raw_job_details_html

    @staticmethod
    def generate_job_details_url(company, job_title, job_id):
        """
        Purpose:
            Get Job Details URL From the company, job_title, and job_id
        Args:
            company (String): Name of the company the job is with
            job_title (String): The title of the position with the company
            job_id (String): The unqiue job_id from Indeed
        Returns:
            job_details_url (String): URL to call to get job details based on
                a job listing
        """

        # Format the variables according to how Indeed Expects them
        company = company.replace(" ", "-")
        job_title = job_title.replace(" ", "-")
        job_id = job_id.replace(" ", "-")

        # Generating the Job Details URLURL
        job_details_url =\
            f"https://www.indeed.com/cmp/{company}/jobs/{job_title}-{job_id}"

        return job_details_url

    ###
    # HTML Parsing
    ###

    @staticmethod
    def parse_job_listings_html(raw_job_listing_html):
        """
        Purpose:
            parse the HTML with Beautiful Soup.
        Args:
            raw_job_listing_html (String): HTML string to parse utilizing beautiful soup.
                Contains the HTML of the job listings
        Return:
            job_listings (List of Dicts): Job listings that have been found
        """

        job_listings = []

        # Parse Main DOM
        job_listing_beautiful_soup = BeautifulSoup(raw_job_listing_html, "html.parser")
        job_listing_cards =\
            job_listing_beautiful_soup.findAll("div", {"class": "jobsearch-SerpJobCard"})

        # Get Each Job Listing
        for job_listing_card in job_listing_cards:
            regex_remove_characters = r"[^A-Za-z0-9\.\-\?\!\,\$\%\&\#\@\^\*\(\)]+"

            try:
                company = re.sub(
                    regex_remove_characters,
                    " ",
                    job_listing_card.find("span", {"class": "company"}).text,
                ).strip()
            except Exception as err:
                company = None

            try:
                job_id = (
                    job_listing_card.find("div", {"class": "sjcl"})
                    .find("div", {"class": "recJobLoc"})
                    .get("id")
                    .lstrip("recJobLoc_")
                    .strip()
                )
            except Exception as err:
                job_id = None

            try:
                job_summary = re.sub(
                    regex_remove_characters,
                    " ",
                    job_listing_card.find("div", {"class": "summary"}).text,
                ).strip()
            except Exception as err:
                job_summary = None

            try:
                job_title = re.sub(
                    regex_remove_characters,
                    " ",
                    job_listing_card.find("div", {"class": "title"}).text,
                ).strip()
            except Exception as err:
                job_title = None

            try:
                job_salary = re.sub(
                    regex_remove_characters,
                    " ",
                    job_listing_card.find("span", {"class": "salary"}).text,
                ).strip()
            except Exception as err:
                job_salary = None

            try:
                re.sub(
                    regex_remove_characters,
                    " ",
                    job_listing_card.find("span", {"class": "iaLabel"}).text,
                ).strip()
                easy_apply = True
            except Exception as err:
                easy_apply = False

            job_listings.append({
                "company": company,
                "job_id": job_id,
                "job_summary": job_summary,
                "job_title": job_title,
                "job_salary": job_salary,
                "easy_apply": easy_apply,
            })

        return job_listings

    @staticmethod
    def parse_job_details_html(raw_job_details_html):
        """
        Purpose:
            Get jobs from Indeed UI. Call the UI and parse the HTML with Beautiful Soup.
        Args:
            job_html (String): HTML string to parse utilizing beautiful soup
        Return:
            job_listings (List of Dicts): Jobs that have been found
        """

        job_details = {}

        # Parse Main DOM
        job_details_beautiful_soup = BeautifulSoup(raw_job_details_html, "html.parser")

        # Get Raw Description
        try:
            raw_job_description = job_details_beautiful_soup.find(
                "div",
                {"id": "jobDescriptionText"}
            )
            job_details["job_description"] = raw_job_description.text.strip()
        except Exception as err:
            job_details["job_description"] = None

        # Get Apply Link
        try:
            raw_job_apply_span = job_details_beautiful_soup.find(
                "span",
                {"id": "originalJobLinkContainer"}
            )
            job_details["job_apply_url"] = raw_job_apply_span.find("a")["href"]
        except Exception as err:
            job_details["job_apply_url"] = None

        # Get When job was posted
        try:

            raw_job_posting_metadata = job_details_beautiful_soup.find(
                "div",
                {"class": "jobsearch-JobMetadataFooter"}
            )

            job_details["job_posting_timeframe"] = None
            for job_metadata_value in raw_job_posting_metadata.text.split("-"):
                if "ago" in job_metadata_value:
                    job_details["job_posting_timeframe"] = job_metadata_value.strip()
                    break

            job_details["job_posting_datetime"] =\
                Indeed.parse_job_posting_datetime(job_details["job_posting_timeframe"])

        except Exception as err:
            job_details["job_posting_timeframe"] = None
            job_details["job_posting_datetime"] = None

        # Get Job Init Data (has interesting Information on the job)
        try:
            start_data_string = "window._initialData="
            start_data_string_location =\
                raw_job_details_html.find(start_data_string) + len(start_data_string)
            stripped_raw_job_details_html =\
                raw_job_details_html[start_data_string_location:]
            end_data_string = ";</script>"
            end_data_string_location =\
                stripped_raw_job_details_html.find(end_data_string)
            raw_init_data = stripped_raw_job_details_html[:end_data_string_location]
            job_details["init_data"] = json.loads(raw_init_data)
        except Exception as err:
            job_details["init_data"] = {}

        # Get Job Location (from init_data)
        try:
            location_string = job_details["init_data"].get("jobLocation", None)

            if not location_string:
                job_details["city"] = None
                job_details["state"] = None
                job_details["zip_code"] = None
            else:

                if location_string.split()[-1].strip().isdigit():
                    job_details["zip_code"] = location_string.split()[-1].strip()
                    location_string = " ".join(location_string.split()[:-1])
                else:
                    job_details["zip_code"] = None

                if "," in location_string:
                    job_details["city"] = location_string.split(",")[0].strip()
                    job_details["state"] = location_string.split(",")[-1].strip()
                else:
                    job_details["city"] = location_string
                    job_details["state"] = None

        except Exception as err:
            job_details["city"] = None
            job_details["state"] = None
            job_details["zip_code"] = None

        # College Degree
        if not job_details["job_description"]:
            job_details["college_degree"] = "Not Specified"
        elif "associates" in job_details["job_description"]:
            job_details["college_degree"] = "Associates"
        elif "bachelor" in job_details["job_description"]:
            job_details["college_degree"] = "Bachelor's"
        else:
            job_details["college_degree"] = "Not Specified"

        return job_details

    ###
    # HTML Parsing
    ###

    @staticmethod
    def parse_job_posting_datetime(job_posting_timeframe):
        """
        Purpose:
            parse the job posting timeframe into a date
        Args:
            job_posting_timeframe (String): How long ago the job was posted
        Return:
            job_posting_datetime (Datetime OBj): Datetime of the job posting
        """

        current_date = datetime.now()
        job_posting_datetime = None

        if not job_posting_timeframe:
            job_posting_date = current_date - timedelta(days=31)
        elif "hour" in job_posting_timeframe:
            hours_ago = int(job_posting_timeframe.split()[0])
            job_posting_datetime = current_date - timedelta(hours=hours_ago)
        elif "day" in job_posting_timeframe:
            if "30+" in job_posting_timeframe:
                days_ago = 31
            else:
                days_ago = int(job_posting_timeframe.split()[0])
            job_posting_datetime = current_date - timedelta(days=days_ago)

        return job_posting_datetime

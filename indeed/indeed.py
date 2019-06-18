#!/usr/bin/env python3
"""
    Purpose:
        The Indeed class is responsible for connecting to Indeed.com and using the tool
        to find jobs.
"""

# Python Library Imports
import logging
import re
import requests
from bs4 import BeautifulSoup


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
            job_listings = Indeed.parse_jobs_from_job_results(raw_job_listing_html)
        else:
            logging.error(f"Failed to Fetch HTML from Indeed URL, exiting")
            job_listings = []

        # Get More Information For Each Job Listing
        for job_listing in job_listings:

            # Add Job Type As A Field
            job_listing["job_type"] = job_type

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
        company = company.replace(" ", "-")
        job_title = job_title.replace(" ", "-")
        job_id = job_id.replace(" ", "-")
        logging.info(f"Getting Metadata for {company}: {job_title}-{job_id}")

        job_details = {}

        job_url = f"https://www.indeed.com/cmp/{company}/jobs/{job_title}-{job_id}"
        job_details["job_url"] = job_url

        # Get the HTML from the URL

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
            parsing the results into a variabl. Search for jobs using
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

    ###
    # HTML Parsing
    ###

    @staticmethod
    def parse_jobs_from_job_results(job_html):
        """
        Purpose:
            Get jobs from Indeed UI. Call the UI and parse the HTML with Beautiful Soup.
        Args:
            job_html (String): HTML string to parse utilizing beautiful soup
        Return:
            job_listings (List of Dicts): Jobs that have been found
        """

        job_listings = []

        beautiful_soup = BeautifulSoup(job_html, "html.parser")

        # job_cards = beautiful_soup.find("div", {"data-tn-component": "organicJob"})
        # job_cards = beautiful_soup.findAll("div", {"class": "result-link-bar"})
        job_cards = beautiful_soup.findAll("div", {"class": "jobsearch-SerpJobCard"})
        for job_card in job_cards:
            text_cleaner_regex = r"[^A-Za-z0-9\.\-\?\!\,\$\%\&\#\@\^\*\(\)]+"

            try:
                company = re.sub(
                    text_cleaner_regex,
                    " ",
                    job_card.find("span", {"class": "company"}).text,
                ).strip()
            except Exception as err:
                company = "-"
            try:
                job_id = (
                    job_card.find("div", {"class": "sjcl"})
                    .find("div", {"class": "recJobLoc"})
                    .get("id")
                    .lstrip("recJobLoc_")
                    .strip()
                )
            except Exception as err:
                job_id = "-"
            try:
                job_summary = re.sub(
                    text_cleaner_regex,
                    " ",
                    job_card.find("div", {"class": "summary"}).text,
                ).strip()
            except job_summary as err:
                job_summary = "-"
            try:
                job_title = re.sub(
                    text_cleaner_regex,
                    " ",
                    job_card.find("div", {"class": "title"}).text,
                ).strip()
            except Exception as err:
                job_title = "-"
            try:
                job_salary = re.sub(
                    text_cleaner_regex,
                    " ",
                    job_card.find("div", {"class": "salary"}).text,
                ).strip()
            except Exception as err:
                job_salary = "-"
            try:
                re.sub(
                    text_cleaner_regex,
                    " ",
                    job_card.find("span", {"class": "iaLabel"}).text,
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
                "date_posted": "-",
                "city": "-",
                "state": "-",
                "zip_code": "-",
            })

        return job_listings

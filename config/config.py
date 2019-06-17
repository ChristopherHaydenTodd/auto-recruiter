"""
    Purpose:
        Configuration Class is responsible for holding the configuration of the project
        and creating a process for pulling tiered configuration through subclasses
"""

# Python Library Imports
import logging
import os


###
# Configuration Class
###


class Config():
    """
        Base Config Class. responsible for holding the configuration of the project
        and creating a process for pulling tiered configuration through subclasses
    """

    @classmethod
    def get(cls, environment=None):
        """
        Purpose:
            Get specific config instance

            This method will use the value of the env argument (if provided)
            to determine which configuration tier to use.  If not supplied,
            the method will default to the tier that can be determined from
            the hostname command.
        Args:

        Returns:
            CONFIGS (Config Obj): Object of the config class specfied from the
                environmental variable or the  argument. Defaults to development
                if nothing is set
        """

        if not environment:
            environment = os.getenv("ENVIRONMENT", "development")

        if environment in ('prod', 'production'):
            CONFIGS = cls.Production()
        elif environment in ('uat'):
            CONFIGS = cls.Uat()
        elif environment in ('test', 'testing', 'qa'):
            CONFIGS = cls.Qa()
        elif environment in ('dev', 'development'):
            CONFIGS = cls.Development()
        else:
            logging.warn(f"{environment} is not a vaild tier, defaulting to development")
            CONFIGS = cls.Development()

        return CONFIGS

    class Production():
        """
            Production instance of base class
        """

        ENVIRONMENT = 'production'

        ###
        # Logging
        ###

        LOG_LEVEL = logging.INFO

    class Uat(Production):
        """
        Purpose:
            UAT instance of base class. Used for customer facing testing. Post release
            candidate testing.
        """

        ENVIRONMENT = 'uat'

    class Qa(Uat):
        """
        Purpose:
            Qa instance of base class. Used for QA of the code (developer testing) and
            release candidate testing. Non-customer facing.
        """

        ENVIRONMENT = "qa"

    class Development(Qa):
        """
        Purpose:
            Development instance of base class. Used as the sandbox of the proeject, for
            local testing, or proof of concepts.
        """

        ENVIRONMENT = "development"

        ###
        # Logging
        ###

        LOG_LEVEL = logging.DEBUG

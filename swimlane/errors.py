"""Custom exceptions and errors"""

from difflib import get_close_matches

from requests import HTTPError


class SwimlaneError(Exception):
    """Base exception for Swimlane errors"""


class UnknownField(SwimlaneError, KeyError):
    """Raised anytime access is attempted to a field that does not exist on an App or Record"""

    def __init__(self, app, field_name, field_pool):
        self.app = app
        self.field_name = field_name
        self.similar_field_names = get_close_matches(self.field_name, field_pool, 3)

        message = "App '{}' has no field '{}'".format(self.app, self.field_name)

        if self.similar_field_names:
            message += '. Similar fields: ' + ', '.join([repr(f) for f in self.similar_field_names])

        super(UnknownField, self).__init__(message)


class InvalidServerVersion(SwimlaneError, ValueError):
    """Raised when method requiring a specific server version range is called when connected to server outside range"""

    def __init__(self, swimlane, min_version, max_version):
        self.swimlane = swimlane
        self.min_version = min_version
        self.max_version = max_version

        if self.min_version and self.max_version:
            message = 'between {} - {}'.format(self.min_version, self.max_version)
        elif self.min_version:
            message = '>= {}'.format(self.min_version)
        else:
            message = '<= {}'.format(self.max_version)

        super(InvalidServerVersion, self).__init__('Server version {} must be '.format(swimlane.version) + message)


class SwimlaneHTTP400Error(SwimlaneError, HTTPError):
    """Exception raised when receiving a 400 response with additional context"""

    codes = {
        -1: 'Unknown',
        1000: 'PasswordExpired',
        1001: 'DuplicateUserName',
        1002: 'InvalidUserNameOrPassword',
        1003: 'ConfirmPasswordDoesNotMatch',
        1004: 'PasswordDoesNotMeetComplexityRequirements',
        1005: 'PasswordResetRequired',
        1006: 'NewPasswordCannotMatchCurrent',
        1007: 'InvalidUser',
        1051: 'DuplicateGroupName',
        1061: 'DuplicateRoleName',
        2000: 'DuplicateFieldName',
        2001: 'FieldNameEmpty',
        2002: 'InvalidApplicationExportFile',
        2003: 'ApplicationNotFound',
        2004: 'InvalidCalculation',
        3000: 'DuplicateFieldValue',
        3001: 'InvalidDateField',
        3002: 'RecordNotFound',
        3003: 'FieldNotFound',
        4000: 'BadStatsGroup',
        4001: 'BadFilter',
        5000: 'AppLimitExceeded',
        5001: 'UserLimitExceeded',
        5002: 'NewServerInstall',
        5003: 'UnableToConnectToActiveDirectory',
        5004: 'UnableToRetrieveStoredValue',
        5005: 'UnableToConnectToMongoDb',
        5006: 'UnableToConnectToSmtp',
        5007: 'SwimlaneAlreadyInitialized',
        5008: 'ModelValidationError',
        5009: 'UpgradeInProcess',
        5010: 'RequiredFieldMissing',
        6000: 'ConnectionDataNotProvided',
        7000: 'RegexNotDefined',
        7001: 'AssetNotFound',
        9000: 'BadThreatIntelConnector',
        9001: 'NoThreatIntel',
        9002: 'ThreatIntelTypeNotSupportedByThisProvider',
        10000: 'DuplicateTaskName',
        10001: 'TaskNotFound'
    }

    def __init__(self, http_error):
        self.http_error = http_error

        try:
            error_content = self.http_error.response.json()
        except ValueError:
            error_content = {'Argument': None, 'ErrorCode': '-1'}

        self.code = int(error_content['ErrorCode'])
        self.argument = error_content['Argument']
        self.name = self.codes.get(self.code, self.codes[-1])

        if self.argument is None:
            message = self.name
        else:
            message = '{name} ({argument})'.format(name=self.name, argument=self.argument)

        super(SwimlaneHTTP400Error, self).__init__(
            '{message}: Bad Request for url: {url}'.format(message=message, url=self.http_error.response.url)
        )

import os

GAR_NEXMO_API_KEY    = os.environ.get('GAR_NEXMO_API_KEY', None)
GAR_NEXMO_API_SECRET = os.environ.get('GAR_NEXMO_API_SECRET', None)
GAR_NEXMO_PHONE_NO   = os.environ.get('GAR_NEXMO_API_PHONE_NO', None)

WIT_ACCESS_TOKEN = os.environ.get('GAR_WIT_ACCESS_TOKEN')

SQLITE_DATABASE      = 'data/data.db'
BUIlDING_NAME_LOOKUP = 'data/buildings.json'

# Log files
LOGGER_SERVER  = 'logs/server.log'
LOGGER_SERVICE = 'logs/getaroom.log'

# These numbers will be blocked
BLACKLIST = 'config/blacklist.json'

# These numbers will never be rate limited
ADMIN_LIST = 'config/admins.json'

# Print texts to console instead of sending SMS
DEBUG_SMS = True

# 10 texts an hour
SMS_PER_PERIOD = 10
SMS_PERIOD     = 3000

# Send warning message when a user has become rate limited. No penalty
RATE_LIMIT_WARNING_MESSAGE = True

# Count if a generic text consumes more than one message (long building name)
SMS_LARGE_PENALTY = False

DICTIONARY_FILE = "config/dictionary.json"
DEFAULT_LANGUAGE = "en"

# Maintain a log of all inbound and outbound messages in the database
# Also logs phone numbers
LOG_MESSAGES = True
from enum import Enum


class QueueCollection(Enum):
    GENERAL_QUEUE = 'general_urls'
    SEMI_SPECIFIC_QUEUE = 'semi_specific_urls'
    SPECIFIC_QUEUE = 'specific_urls'


UPLOAD_FOLDER = r'app\src\uploads'

SPECIFIC_DOMAINS = ['wikipedia']
SEMI_SPECIFIC_DOMAIN_NAMES = ['worldhistory',
                             'magazine',
                             'theguardian',
                             'indeed',
                             'mckinsey',
                             'medicalnewstoday',
                             'science'
                              ]
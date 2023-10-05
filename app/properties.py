from enum import Enum


class QueueCollection(Enum):
    GENERAL_QUEUE = 'general_urls'
    SEMI_SPECIFIC_QUEUE = 'semi_specific_urls'
    SPECIFIC_QUEUE = 'specific_urls'


UPLOAD_FOLDER = r'app/uploads'


SEMI_SPECIFIC_DOMAIN_NAMES = ['sankalpindia',
                              'science',
                              'geographynotes',
                              'paris2024',
                              'pib',
                              'kids',
                              'walnutfolks',
                              'un',
                              'brahmakumaris',
                              'risingkashmir',
                              'survivalinternational',
                              'jagranjosh',
                              'education',
                              'indeed',
                              'noaa',
                              'linkedin'
                              ]

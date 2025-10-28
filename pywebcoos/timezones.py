import numpy as np


TIMEZONES_BY_STATE = {'ME': 'America/New_York',
                      'NH': 'America/New_York',
                      'MA': 'America/New_York',
                      'RI': 'America/New_York',
                      'CT': 'America/New_York',
                      'NY': 'America/New_York',
                      'NJ': 'America/New_York',
                      'PA': 'America/New_York',
                      'DE': 'America/New_York',
                      'MD': 'America/New_York',
                      'VA': 'America/New_York',
                      'NC': 'America/New_York',
                      'SC': 'America/New_York',
                      'GA': 'America/New_York',
                      'FL': 'America/New_York',
                      'OH': 'America/New_York',
                      'AL': 'America/Chicago',
                      'MS': 'America/Chicago',
                      'LA': 'America/Chicago',
                      'TX': 'America/Chicago',
                      'MI': 'America/Chicago',
                      'IL': 'America/Chicago',
                      'IN': 'America/Chicago',
                      'WI': 'America/Chicago',
                      'WA': 'America/Los_Angeles',
                      'OR': 'America/Los_Angeles',
                      'CA': 'America/Los_Angeles',
                      'AK': 'America/Nome',
                      'HI': 'US/Hawaii'}


def from_name(camera_name):
    sbool = [' '+k in camera_name for k in list(TIMEZONES_BY_STATE.keys())]
    if np.sum(sbool) > 0:
        state_abbrev = np.array(list(TIMEZONES_BY_STATE.keys()))[sbool][0]
        return TIMEZONES_BY_STATE[state_abbrev]
    else:
        raise ValueError('Camera name does not contain state abbreviation')
    


    

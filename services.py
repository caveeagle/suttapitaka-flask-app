import time
import sys
import os

#############################################################
#############################################################

def get_lock_path(app_name='myapp'):

    if os.name == 'posix':  # Debian
        return os.path.join('/run', f'{app_name}.lock')

    else:  # My own local computer (not for all)
        tmp = os.environ.get('TEMP')
        return os.path.join(tmp, f'{app_name}.lock')

#############################################################
#############################################################



#############################################################
#############################################################


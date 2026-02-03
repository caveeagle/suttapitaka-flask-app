import time
import sys
import os
import random
import logging

#############################################################
#############################################################

REQUESTS_INTERVAL = 20  # In seconds

#############################################################
#############################################################

def get_lock_path(app_name='suttapitaka'):
    
    if os.environ.get('IN_DOCKER'):
        return f'/app/run/{app_name}.lock'
    elif os.name == 'posix':
        return f'/run/suttapitaka/{app_name}.lock'
    else:
        return os.path.join(os.environ['TEMP'], f'{app_name}.lock')
        
#############################################################
#############################################################

logger = logging.getLogger('sutra')
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)

#############################################################
#############################################################

def get_uid() -> str:  # get uniq id for cookies

    return random.randint(1, 10_000)
    
    '''
    Also we can use this:  uuid.uuid4()
    but short int num more convinient now
    '''

def web_logging(request:str, cid: int = 0, ip: str = ''):
    
    logger.info(f'[SUTRA] ~~~~~~~~~~')
    logger.info(f'[SUTRA] [IP] {ip}')
    logger.info(f'[SUTRA] [CID] {cid}')
    logger.info(f'[SUTRA] [REQ] {request}')
    logger.info(f'[SUTRA] ----------')
    
    return

#############################################################
#############################################################


def get_api_key():
    
    API_KEY = os.environ.get('GEMINI_API_KEY')

    if not API_KEY:
        
        print('There is no such variable: GEMINI_API_KEY',)    
    
    return API_KEY

#############################################################
#############################################################

TIMER_FILE = 'last.request.time.txt'

def setTime4RateLimit():

    now_str = time.strftime('%d.%m.%Y - %H:%M:%S', time.localtime())
    now_sec = str(int(time.time()))

    with open(TIMER_FILE, 'w') as f:
        f.write(now_str+'\n')
        f.write(now_sec+'\n')
    
    return


def validateRateLimit() -> bool:
    
    last_access = 0
    
    try:

        with open(TIMER_FILE) as f:
            next(f)
            last_access = int(f.readline())
    
    except FileNotFoundError:
        last_access = 0
            
    now = int(time.time())   
    
    delta = now - last_access
    
    if delta < REQUESTS_INTERVAL:
        
        return False
    
    else:       
    
        setTime4RateLimit()
        return True
    
#############################################################
#############################################################


def main():
    
    pass

if __name__ == '__main__':
    main()


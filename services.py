import time
import sys
import os
import random
import logging
import sqlite3

#############################################################
#############################################################

REQUESTS_INTERVAL = 2  # In seconds

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

logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)],
)

#############################################################
#############################################################

def get_uid() -> str:  # get uniq id for cookies

    return random.randint(1, 10_000)
    
    '''
    Also we can use this:  uuid.uuid4()
    but short int num more convinient now
    '''

#############################################################
#############################################################

BUCKET_NAME = 'suttapitaka-logs'

BLOB_NAME = 'web-logging.sqlite'

LOCAL_FILE = BLOB_NAME

try:
    
    from google.cloud import storage

    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(BLOB_NAME)
    blob.download_to_filename(LOCAL_FILE)
    
    logging.info('SQLite DB downloaded')
    
except Exception as e:
    print("Something failed with logging:", type(e).__name__, "-", e)

#############################################################
#############################################################

def web_logging(request:str, cid: int = 0, ip: str = '-'):
    
    now_str = time.strftime('%d.%m.%Y - %H:%M:%S', time.localtime())
    
    logging.info(f'[SUTRA] ~~~~~~~~~~')
    logging.info(f'[SUTRA] [DATETIME] {now_str}')
    logging.info(f'[SUTRA] [IP] {ip}')
    logging.info(f'[SUTRA] [CID] {cid}')
    logging.info(f'[SUTRA] [REQ] {request}')
    logging.info(f'[SUTRA] ----------')
    
    ###################################
    
    db = 'web-logging.sqlite'

    try:
    
        with sqlite3.connect(LOCAL_FILE) as conn:
        
            conn.execute(
                '''
                INSERT INTO requests (cid, ip, request)
                VALUES (?, ?, ?)
                ''',
                (cid, ip, request)
            )
            conn.commit()
        
        blob.upload_from_filename(LOCAL_FILE)
        
        logging.info('Web logging done')

    except Exception as e:
        print('Upload failed:', type(e).__name__, ' - ', e)
    
    ###################################
    
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


import time
import sys
import os

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
    
    DEBUG = 0
    
    if DEBUG:
        print(f'Delta: {delta}')
    
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


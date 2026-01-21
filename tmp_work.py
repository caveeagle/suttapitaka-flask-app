import fasteners
import os

def get_lock_path(app_name='myapp'):

    if os.name == 'posix':  # Debian
        return os.path.join('/run', f'{app_name}.lock')

    else:  # My own local computer (not for all)
        tmp = os.environ.get('TEMP')
        return os.path.join(tmp, f'{app_name}.lock')

################################################

lock_path = services.get_lock_path('suttapitaka')

lock = fasteners.InterProcessLock(lock_path)

if not lock.acquire(blocking=False):
    print('Process blocked')
    raise SystemExit(1)

try:

    pass

finally:
    
    lock.release()    


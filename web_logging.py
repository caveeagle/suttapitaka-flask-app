import sqlite3
import random

#############################################################
#############################################################

db = 'web-logging.sqlite'

    
#############################################################
#############################################################

def web_logging(request:str, cid: int = 0, ip: str = ''):
    
   with sqlite3.connect(db) as conn:

        conn.execute(
            '''
            INSERT INTO requests (cid, ip, request)
            VALUES (?, ?, ?)
            ''',
            (cid, ip, request)
        )
   
   return

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

def main():
    
    print(un_uid())
    
    
if __name__ == '__main__':
    main()


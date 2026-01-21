import sqlite3

#############################################################
#############################################################

db_name = 'web-logging.sqlite'

    
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

def main():
    
    web_logging('req')
    web_logging('req',1,'1.1.1.1')
    
if __name__ == '__main__':
    main()


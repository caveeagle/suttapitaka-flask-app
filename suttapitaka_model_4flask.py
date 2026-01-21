import time
import sys
import os
import sqlite3

import fasteners
import numpy as np
from google import genai
from google.genai.errors import ClientError
import secret_config
from model_indexing import build_index, search

#########################################################
#########################################################

TOP_K = 5

TEMPERATURE = 0.5

MODEL = 'gemini-2.5-pro'

FIRST_DELAY = 0.5 #  In seconds

SECOND_DELAY = 2

#########################################################
#########################################################

PROMPT_TEMPLATE = """
You answer questions using ONLY the provided sources.

Each source is marked as [CHAPTER <id>].

Rules:
- Use ONLY information that is explicitly present in the sources.
- If the answer is NOT present in the sources, output exactly:
  The answer is not found in the provided sources.
- Do NOT use outside knowledge.
- Do NOT invent sources.
- Do NOT invent CHUNK IDs.
- Follow the output format exactly.

Question:
{question}

Sources:
{sources}

Output format (must be exact):

<answer OR the no-answer sentence>

Sources:
<comma-separated CHAPTER IDs, or empty if no answer>
"""

#########################################################
#########################################################

def suttapitaka_answer(QUESTION:str):    
    
    API_KEY = secret_config.API_KEY
    
    if not API_KEY or not API_KEY.strip():
        raise ValueError('API_KEY is empty or not set')
    
    client = genai.Client(api_key=API_KEY)
    
    index, chunk_ids = build_index()
    
    resp = client.models.embed_content(
        model='models/text-embedding-004',
        contents=[QUESTION],
    )
    
    time.sleep(FIRST_DELAY)
    
    query_vec = np.array(resp.embeddings[0].values, dtype=np.float32)
    
    top_chunk_ids, scores = search(index, chunk_ids, query_vec, k=TOP_K)
    
    assert len(top_chunk_ids) == TOP_K 
    
    #########################################################
    #########################################################
    
    db = 'sutta-pitaka.sqlite'
    
    context_lines = []
    
    placeholders = ','.join('?' for _ in top_chunk_ids)
    
    query = f'''
    SELECT *
    FROM chunks
    WHERE id IN ({placeholders})
    ORDER BY id
    '''
    
    with sqlite3.connect(db) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
    
        cursor.execute(query, top_chunk_ids)
        rows = cursor.fetchall()
        
    content_blocks = []
    
    for row in rows:
        content_blocks.append(
            f"[CHAPTER {row['chapter']}]\n{row['content']}"
        )
    
    SOURCES = '\n\n'.join(content_blocks)
    
    assert len(content_blocks) == TOP_K
    
    #########################################################
    #########################################################
    
    PROMPT = PROMPT_TEMPLATE.format(
        question=QUESTION,
        sources=SOURCES
    )
    
    try:
        
        response = client.models.generate_content(
            model=MODEL,
            contents=[PROMPT],
            config={
                'temperature': TEMPERATURE
            }        
        )
        
        time.sleep(SECOND_DELAY)
        
    except ClientError as e:
        msg = str(e)
    
        if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
            print(f'ERROR 429 - LIMITS EXCEEDED!')
            # просто выходим, ничего не выводим
            pass
        else:
            raise
        
    #########################################################
    
    return response.text

#########################################################
#########################################################

def get_lock_path(app_name='myapp'):

    if os.name == 'posix':  # Debian
        return os.path.join('/run', f'{app_name}.lock')

    else:  # My own local computer (not for all)
        tmp = os.environ.get('TEMP')
        return os.path.join(tmp, f'{app_name}.lock')

#########################################################
#########################################################

def suttapitaka_answer_with_logging(QUESTION:str):
    '''
        Add another wrapper layer around the function,
        for logging and locking!
    '''

    lock_path = get_lock_path('suttapitaka')
    
    lock = fasteners.InterProcessLock(lock_path)
    
    if not lock.acquire(blocking=False):
        
        return('The request has been blocked — too many requests! \n Please wait and try again later.')

    ANSW = '...'
    
    try:
    
        ANSW = suttapitaka_answer(QUESTION)
    
    except Exception as e:

        print(f'Error: {e}')

        ANSW = 'Error: smth went wrong...'
    
    finally:
        
        lock.release()    

    return ANSW    

#########################################################
#########################################################


def main():

    QUESTION = 'Can a woman become an Arahant?'
    
    print(f'QUESTION: {QUESTION}')
    
    ANSWER = suttapitaka_answer_with_logging(QUESTION)
    
    print(ANSWER)
    
    print(f'\nJob finished')

#########################################################
#########################################################

if __name__ == "__main__":
    main()
#########################################################

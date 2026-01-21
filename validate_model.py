import time
import sys
import sqlite3
import numpy as np

from google import genai
from google.genai.errors import ClientError

import secret_config

from model_indexing import build_index, search


#########################################################
#########################################################

####  MODE OF SCRIPT:  ###

MODE = 'VALIDATION'

#MODE = 'TESTING'

'''

TESTING - give the last question, and just show the answer

VALIDATION - test all questions, and compare answers with true answ.

'''


#####  MODEL PARAMETERS:   #####  

TOP_K = 5

TEMPERATURE = 0.5

MODEL = 'gemini-2.5-pro'

FIRST_DELAY = 0.5 #  In seconds

SECOND_DELAY = 2

#####  QUESTION FOR VALIDATION:   #####

QUESTIONS_MAP = {  # ORDER IS IMPORTANT !
    1: 'According to the Buddha, which sensory experiences most strongly occupy a man’s mind?',
    2: 'Can a health monk eat after noon?',
    3: 'In which year was the Buddha born?',
    4: 'Can a woman become an Arahant?',
}

QUESTIONS = [QUESTIONS_MAP[i] for i in sorted(QUESTIONS_MAP)]

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

print(f'Begin to work...\n')

is_passed = True

for Q_NUM, QUESTION in enumerate(QUESTIONS, start=1):    
    
    if MODE == 'TESTING':
        
         QUESTION = QUESTIONS[len(QUESTIONS)-1] #  the last
    
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
    
    if MODE == 'TESTING':
        print(f'Question embedded!')
    
    query_vec = np.array(resp.embeddings[0].values, dtype=np.float32)
    
    top_chunk_ids, scores = search(index, chunk_ids, query_vec, k=TOP_K)
    
    assert len(top_chunk_ids) == TOP_K 
    
    if(0):
        print(f'Find top chunks ids: {top_chunk_ids}')
    
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
    
    if MODE == 'TESTING':
        print(f'Make content blocks, ready for request:')
    
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
        
    if MODE == 'TESTING':
        print(f'Request finished.\n\n')
        
    #########################################################
    #########################################################
    
    ### OUTPUT:
    
    if MODE == 'TESTING':
        print('\nQUESTION:')
        print(QUESTION)
        print('\nANSWER:')
        print(response.text)
    
    if MODE == 'TESTING':
        break  # only last question

    #########################################################
    #########################################################
    
    ### VALIDATIPN:
    
    if MODE == 'VALIDATION':
        
        answ_text, sources_text = response.text.rsplit('Sources', 1)
        
        if Q_NUM==1:
            
            words = ['sight', 'sound', 'smell', 'taste', 'touch', 'of a woman']

            result_1 = all(word in answ_text for word in words)
            
            result_2 = 'an1.1-10' in sources_text.lower()
            
            result = result_1 and result_2
            
        if Q_NUM==2:

            words = ['commits an offense', 'cooked food', 'wrong time']

            result_1 = all(word in answ_text for word in words)
            
            result_2 = 'pli-tv-bu-vb-pc37' in sources_text.lower()
            
            result =  result_1 and result_2
            
        if Q_NUM==3:
            
            result = "answer is not found" in answ_text
             
        if Q_NUM==4:
            
            result_1 = 'woman is able' in answ_text.lower()
            
            result_2 = 'she is able' in answ_text.lower()
            
            result_3 = 'an8.51' in sources_text.lower()
            
            result =  (result_1 or result_2) and result_3
                
        
        ### RESULT:
        if result:
            
            print(f'Test {Q_NUM} PASSED')
        
        else:    
            
            is_passed = False
            
            print(f'Test {Q_NUM} FAILED')
        
        
#########################################################
#########################################################


if MODE == 'VALIDATION':

    if is_passed:
            print(f'\nALL TESTS PASSED!')
            sys.exit(0)

    else:
            print(f'Some errors were encountered!')
            print(f'\nJob finished')
            sys.exit(1)

else:
    print(f'\nJob finished')
    sys.exit(0)

#########################################################
#########################################################


def suttapitaka_answer(QUESTION:str):    
    
    
    return QUESTION.upper()

#########################################################
#########################################################

def main():

    QUESTION = 'Can a woman become an Arahant?'
    
    print(f'QUESTION: {QUESTION}\n')
    
    ANSWER = suttapitaka_answer(QUESTION)
    
    print(ANSWER)
    
    print(f'\nJob finished')

#########################################################
#########################################################

if __name__ == "__main__":
    main()
#########################################################

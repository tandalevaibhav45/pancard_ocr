import re
from .log_file import logger3
from.Pan_erro_handle import BusinessRuleError
def name_correction(text):
    '''This function used to correct the name and father name'''
    try:
        text=text.strip()
        special_characters_txt = r"[-!@#$%^&*_+{}()\[\]:;<>,.?~`|\\\"';=/1234567890©°—]"
        text_field = re.sub(special_characters_txt, "", text)
        return text_field
    except Exception as e:
        logger3.error(f'{e} on line {e.__traceback__.tb_lineno}')
        raise BusinessRuleError("")
    
def date_pattern(raw_data):
    '''This function is used to correct the date'''
    compare_dict = {'S': '5', 's': '5', 'O': '0', 'o': '0', 'i': '1', 'I': '1', 'L': '1', 'Z': '2', 'z': '2', '(': '', '[': '', ')': '', ']': '', '{': '', '}': '','.':'',',':'','//':'',' ':''}
    raw_data=raw_data.strip()
    raw_data = re.sub("|".join(map(re.escape, compare_dict.keys())), lambda x: compare_dict[x.group()], raw_data)
    if len(raw_data)< 4:
        separator='/'
        if '-' in raw_data:
            separator='-'
        elif '/' in raw_data:
            separator='/'
        raw_data=re.sub(r'[./-]',separator,raw_data)
        date_pattern=re.compile(r'(\d{1,2})[./-]?(\d{1,2})[./-]?(\d{2,4})')
        match=date_pattern.match(raw_data)
        if match:
            day,month, year=match.groups()
            formatted_date= f'{day.zfill(2)}{separator}{month.zfill(2)}{separator}{year.zfill(4)}'
            return formatted_date
        else:
            return raw_data
    else:
        return raw_data
def pan_no_iteration(pan):
    new_pan_str = ''
    compare_dic = {'S': '5', 'O': '0','I': '1', 'L': '1', 'Z': '2'} 
    for pan_no in range(len(pan)):
            if pan_no in [0,1,2,3,4,9]:
                if pan[pan_no].isalpha():
                    new_pan_str+=pan[pan_no]
                else:
                    for key,value in compare_dic.items():
                        if value == pan[pan_no]:
                            new_pan_str+=key
            else:
                if pan[pan_no].isdigit():
                    new_pan_str+=pan[pan_no]
                else:   
                    for key,value in compare_dic.items():
                        if key == pan[pan_no]:
                            new_pan_str+=value
    return new_pan_str

    
def pan_no_correct(extracted_text):
    '''This function corrects the pan number'''
    text=extracted_text.strip()
    special_characters_txt = r"[-!@#$%^&*_+{}\[\]:;<>,.?~`|\\n\"';=©°—]"
    text_field = re.sub(special_characters_txt, "", text)
    pan = text_field.upper()
    try:
        pan_number = pan_no_iteration(pan)
        return pan_number
    except Exception as e:
        logger3.error(f'{e} on line {e.__traceback__.tb_lineno}')
        print("error: incorrect pan no,still forward as it is extracted data.",e)
        return extracted_text 
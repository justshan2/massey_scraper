import base64
import re
from typing import TypedDict

import requests
from bs4 import BeautifulSoup

massey_base = 'https://masseyratings.com' 
url = 'https://masseyratings.com/cf/fbs/ratings'


def get_page_source(url: str) -> str:
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f'failed to fetch page source for URL: {url}')
    return response.text


class Stamp(TypedDict):
    jsoptions: int
    obfu: str
    baseURL: str
    jsonURL: str
    cache_hash: str
    runwhenready: str
    diagnose: int

def extract_stamp_text(page_source: str) -> str:
    soup = BeautifulSoup(page_source, 'lxml')
    text = soup.find_all(name='script', string=re.compile('stamp'), limit=1)[0].text
    return text


def process_stamp_text(stamp_text) -> Stamp:
    text_without_stamp_word = stamp_text.replace('stamp.', '')
    text_without_trailing_semicolon = text_without_stamp_word.strip(';')
    stamp_attrs = text_without_trailing_semicolon.split(';')
    processed_values = {}
    for stamp_attribute in stamp_attrs:
        key, unprocessed_value = stamp_attribute.split('=')
        value = None
        if unprocessed_value[0] == '"':
            value = unprocessed_value.strip('"')
        else:
            value = int(unprocessed_value)
        processed_values[key] = value
    return processed_values

def decode_string(encoded_string, second_arg=2021):
    replaced_string = encoded_string.replace('-', '+').replace('_', '/').replace('.', '=')
    decoded_string = base64.b64decode(replaced_string)
    decrypted_chars = []
    for char in decoded_string:
        second_arg = (8121 * second_arg + 1234) % 256
        decrypted_chars.append((char - second_arg + 256) % 256)
    decrypted_string = ''.join(map(chr, decrypted_chars))
    return decrypted_string

def get_json(jsonURL):
    response = requests.get(jsonURL)
    response_json = response.json()
    return response_json

# json_for_ranking = transform_json(fetched_json)

def process_json(json, stamp):
    ti = json['TI']
    # print(ti)
    ci = json['CI']
    if 'RI' in json:
        ri = json['RI']
        if 'length' in ri:
            hasRI = 1
    
    di = json['DI']
    # print('ci', ci)
    # print('di', di)
    # print('ri', ri)
    if stamp['jsoptions'] & 4 and len(di) > 0: 
        referenceValue = int(stamp['obfu'][32:]) #obfu last three digits
        for i in range(len(ci)):
            gfacValue = ci[i]['gfac']
            if not gfacValue:
                continue
            
            diValueWasArray = isinstance(di[0][i], list)
            for j in range(len(di)):
                referenceValue = (8121 * referenceValue + 1234) % (1024)
                if diValueWasArray: diValue = di[j][i][0]
                else: diValue = di[j][i]

                if diValue is not None:
                    if gfacValue == 1:
                        diValue -= referenceValue
                    elif gfacValue == 2:
                        diValue /= referenceValue + 1
                    else:
                        diValue = decode_string(diValue, referenceValue)
                if diValueWasArray:
                    di[j][i][0] = diValue
                else:
                    di[j][i] = diValue
    return di
                
def post_processing(data):
    ## remove extraneous information
    for element in data:
        element[0] = element[0][0]
        element[1] = element[1][0]
    return data

if __name__ == '__main__':
    #get page source
    source = get_page_source(url)

    #process stamp
    stamp = extract_stamp_text(source)
    stamp_processed = process_stamp_text(stamp)

    #get url of json
    decoded_json_url = decode_string(stamp_processed['jsonURL'])
    full_url = massey_base + decoded_json_url

    #get json
    response_json = get_json(full_url)
    #process json
    data = process_json(response_json, stamp_processed)
    data_processed = post_processing(data)






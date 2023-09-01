import re
from easygoogletranslate import EasyGoogleTranslate


def break_sentence(sentence):
    words = re.findall(r'\b[ঀ-৾]{2,}(?!\w)', sentence, re.UNICODE)
    return words

def translate_pair(source_language, target_language, text):
    translator = EasyGoogleTranslate(
        source_language=source_language,
        target_language=target_language,
        timeout=10
    )
    bn_array = break_sentence(text)
    
    en_array = eval(translator.translate(str(bn_array)))

    rstr = ''
    for word, translation in zip(bn_array, en_array):
            rstr += f'{word} - {translation}\n'

    return rstr

test_text = 'বাল কি তা কি তুমি চিনো ?'


print(translate_pair('bn', 'en', test_text))



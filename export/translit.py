
def transliterate(string):

    capital_letters = {'А': 'A',
                       'Б': 'B',
                       'В': 'V',
                       'Г': 'G',
                       'Д': 'D',
                       'Е': 'E',
                       'Ё': 'E',
                       'Ж': 'Zh',
                       'З': 'Z',
                       'И': 'I',
                       'Й': 'Y',
                       'К': 'K',
                       'Л': 'L',
                       'М': 'M',
                       'Н': 'N',
                       'О': 'O',
                       'П': 'P',
                       'Р': 'R',
                       'С': 'S',
                       'Т': 'T',
                       'У': 'U',
                       'Ф': 'F',
                       'Х': 'H',
                       'Ц': 'Ts',
                       'Ч': 'Ch',
                       'Ш': 'Sh',
                       'Щ': 'Sch',
                       'Ъ': '',
                       'Ы': 'Y',
                       'Ь': '',
                       'Э': 'E',
                       'Ю': 'Y',
                       'Я': 'Ya',}

    lower_case_letters = {'а': 'a',
                       'б': 'b',
                       'в': 'v',
                       'г': 'g',
                       'д': 'd',
                       'е': 'e',
                       'ё': 'e',
                       'ж': 'zh',
                       'з': 'z',
                       'и': 'i',
                       'й': 'y',
                       'к': 'k',
                       'л': 'l',
                       'м': 'm',
                       'н': 'n',
                       'о': 'o',
                       'п': 'p',
                       'р': 'r',
                       'с': 's',
                       'т': 't',
                       'у': '',
                       'ф': 'f',
                       'х': 'h',
                       'ц': 'ts',
                       'ч': 'ch',
                       'ш': 'sh',
                       'щ': 'sch',
                       'ъ': '',
                       'ы': 'y',
                       'ь': '',
                       'э': 'e',
                       'ю': 'y',
                       'я': 'ya',}

    translit_string = ""

    for index, char in enumerate(string):
        if char in lower_case_letters.keys():
            char = lower_case_letters[char]
        elif char in capital_letters.keys():
            char = capital_letters[char]
            if len(string) > index+1:
                if string[index+1] not in lower_case_letters.keys():
                    char = char.upper()
            else:
                char = char.upper()
        translit_string += char

    return translit_string

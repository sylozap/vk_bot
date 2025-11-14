import pytesseract
from typing import Set

class Config:
    TOKEN = "vk1.a.WzyJNgN65NxUJSBhGzOFEO0J5zK3HTdRiMPgiV4HbFJx3R6gAjjeW-nzj2x0WDT3baYjOhhFK8_4gzHr5AxjWdUriFpDRw0yUJp3SJEwJOhC_jSAIn_1pqI2BxyaH3xpcBqGyXJ1OU2Y_2Pti3O7p6vqW1zEJ-hZwrcTdPFqxAr0CIS9e1xqgh-6qUwcOG3w11JVhhweiaA9i1Xm3X2kNw"
    GROUP_ID = "233852854"
    BANDIT_ID = -166948584

    pytesseract.pytesseract.tesseract_cmd = r'C:\Tesseract-OCR\tesseract.exe'

    POSSIBLE_NUMBERS: Set[int] = set(range(37))

    MAX_HISTORY_SIZE = 500
    HISTORY_FILE_PATH = 'history.txt'
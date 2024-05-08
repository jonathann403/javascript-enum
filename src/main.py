import requests
from bs4 import BeautifulSoup
import jsbeautifier
import sys
import re

REGEX_STR = r"""

  (?:"|')                               # Start newline delimiter

  (
    ((?:[a-zA-Z]{1,10}://|//)           # Match a scheme [a-Z]*1-10 or //
    [^"'/]{1,}\.                        # Match a domainname (any character + dot)
    [a-zA-Z]{2,}[^"']{0,})              # The domainextension and/or path

    |

    ((?:/|\.\./|\./)                    # Start with /,../,./
    [^"'><,;| *()(%%$^/\\\[\]]          # Next character can't be...
    [^"'><,;|()]{1,})                   # Rest of the characters can't be

    |

    ([a-zA-Z0-9_\-/]{1,}/               # Relative endpoint with /
    [a-zA-Z0-9_\-/.]{1,}                # Resource name
    \.(?:[a-zA-Z]{1,4}|action)          # Rest + extension (length 1-4 or action)
    (?:[\?|#][^"|']{0,}|))              # ? or # mark with parameters

    |

    ([a-zA-Z0-9_\-/]{1,}/               # REST API (no extension) with /
    [a-zA-Z0-9_\-/]{3,}                 # Proper REST endpoints usually have 3+ chars
    (?:[\?|#][^"|']{0,}|))              # ? or # mark with parameters

    |

    ([a-zA-Z0-9_\-]{1,}                 # filename
    \.(?:php|asp|aspx|jsp|json|
         action|html|js|txt|xml)        # . + extension
    (?:[\?|#][^"|']{0,}|))              # ? or # mark with parameters

  )

  (?:"|')                               # End newline delimiter

"""

def main():
    url = sys.argv[1]

    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.text)
    except Exception as e:
        print(e)
        exit()

    js_files_arr = [i.get('src') for i in soup.find_all('script') if i.get('src')]

    for i in range(len(js_files_arr)):
        js_url = js_files_arr[i]

        if js_url.startswith('.') or js_url.startswith('/'):
            js_url = url + js_url

        r = requests.get(js_url)
        content = jsbeautifier.beautify(r.text)
        regex = re.compile(REGEX_STR, re.VERBOSE)

        all_matches = [(m.group(1)) for m in re.finditer(regex, content) if m.group(1).__contains__('.')]
        print(js_url)
        print(all_matches)

if __name__ == '__main__':
    main()
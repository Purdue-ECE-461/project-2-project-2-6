import base64
import sys

with open('./package_registry/.env', 'wb') as result:
        result.write(base64.b64decode(sys.argv[1]))
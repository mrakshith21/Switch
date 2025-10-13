import os
import re

from tools import read_file, write_file, list_directory, grep
from indexer import query_index 


# print(list_directory('./test'))
# print(grep('./test', '[Cc]alculator'))
write_file('./test/test.txt', 'Hello World! \n What are you doing', insert=True, from_line=1)
import argparse
from indexer import create_index, query_index

parser = argparse.ArgumentParser(description='Switch app params')


# Switch
parser.add_argument('action', type=str,
                    help='index (or) prompt')

parser.add_argument('prompt', type=str, nargs='?',
                    help='Prompt')

args = parser.parse_args()


print("Argument values:")
print(args.action)
print(args.prompt)

if args.action == "index":
    create_index()
elif args.action == "prompt":
    if args.prompt:
        query_index(args.prompt)
    else:
        print("Please provide a prompt for querying the index.")
import argparse
from indexer import create_index, query_index
from coding_agent import run_coding_agent

parser = argparse.ArgumentParser(description='Switch app params')


# Switch
parser.add_argument('action', type=str,
                    help='index (or) prompt')

parser.add_argument('prompt', type=str, nargs='?',
                    help='Prompt')

args = parser.parse_args()

print(args)
if args.action == "index":
    create_index()
elif args.action == "prompt":
    if args.prompt:
        run_coding_agent(args.prompt)
    else:
        print("Please provide a prompt for querying the index.")
elif args.action == "search":
    if args.prompt:
        results = query_index(args.prompt)
    else:
        print("Please provide a search query.")
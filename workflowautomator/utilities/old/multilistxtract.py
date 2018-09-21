import datetime
import pytz
import argparse
import sys
import json

# Allows five lists (none, ready, queue, valid, invalid) to be viewed
# from command line, from json file

if __name__ == '__main__':
    def localized(start):
        timezone = pytz.timezone("America/Chicago")
        for child in start.items():
            for grandchild in child[1]:
                grandchild[1] = timezone.localize(
                    datetime.datetime.fromtimestamp(grandchild[1]))

    parser = argparse.ArgumentParser()
    parser.add_argument("req", help="all, none, ready, queue, valid, invalid")
    parser.add_argument("target", help="object to extract from")
    args = parser.parse_args()

    if args.req not in ('all', 'none', 'ready', 'queue', 'valid', 'invalid'):
        sys.stderr.write("Request is invalid\n")

    with open(args.target, "r") as jsonfile:
        dictio = json.load(jsonfile)
    localized(dictio)
    print("\n")

    if args.req == "all":
        for dictent in dictio:
            print("***" + dictent + "***")
            if len(dictio[dictent]) > 0:
                for i in dictio[dictent]:
                    print(i[0] + "    " + str(i[1]))
                print("\n")
            else:
                print("Nothing here.\n")
    else:
        print("***" + args.req + "***\n")
        if len(dictio[args.req]) > 0:
            for i in dictio[args.req]:
                print(i)
        else:
            print("Nothing here.\n")

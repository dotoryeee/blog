import boto3
from pprint import pprint
import psutil
import csv
import os

# sts = boto3.client("sts")
# response = sts.get_caller_identity()
# pprint(response)

def memory_usage(message: str = "debug"):
    # current process RAM usage
    p = psutil.Process()
    rss = p.memory_info().rss / 2**20  # Bytes to MB
    print(f"[{message}] memory usage: {rss: 10.3f} MB")


CSV_NAME = "test.csv"

def create_test_csv(name):
    fp = open(name, "w")
    w = csv.writer(fp)
    for _ in range(0, 10000000):
        w.writerow([1, 2, 3, 4])

if not os.path.exists(CSV_NAME):
    create_test_csv(CSV_NAME)

memory_usage("START")

fp = open(CSV_NAME)
r = csv.reader(fp)

# list_comp = [i for i in r]  # type: ignore
# list_comp = [tuple(i) for i in r]  # type: ignore
# memory_usage("List Comprehension(Read a File)")

gen_exp = (i for i in r)  # type: ignore
for i in gen_exp:
    memory_usage("Generator Expression(Read a File)")
    # print(i)
# memory_usage("Generator Expression(Read a File)")

memory_usage("END")
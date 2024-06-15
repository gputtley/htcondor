#!/usr/bin/env python3

import sys
import re
import htcondor
from os import makedirs
from os.path import join
from uuid import uuid4

from snakemake.utils import read_job_properties


def camel_to_snake(name):
    # Add an underscore before each uppercase letter (except at the beginning of the string)
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    # Add an underscore before uppercase letters that are followed by lowercase letters or the end of the string
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    # Convert the entire string to lowercase
    return s2.lower()


jobscript = sys.argv[1]
job_properties = read_job_properties(jobscript)

UUID = uuid4()  # random UUID
jobDir = "{{cookiecutter.htcondor_log_dir}}/{}_{}".format(job_properties["jobid"], UUID)
makedirs(jobDir, exist_ok=True)

sub_dict = {
    "executable": "/bin/bash",
    "arguments": jobscript,
    "max_retries": "5",
    "log": join(jobDir, "condor.log"),
    "output": join(jobDir, "condor.out"),
    "error": join(jobDir, "condor.err"),
    "getenv": "True",
}

if "params" in job_properties.keys():
    for line in job_properties["params"]:
        key = line.split("=")[0].replace(" ","")
        val = line.split("=")[1].replace(" ","")
        if "+" in key:
            sub_dict[key] = val
        else:
            sub_dict[camel_to_snake(key)] = val

sub = htcondor.Submit(sub_dict)


schedd = htcondor.Schedd()
clusterID = schedd.submit(sub)

# print jobid for use in Snakemake
print("{}_{}_{}".format(job_properties["jobid"], UUID, clusterID))

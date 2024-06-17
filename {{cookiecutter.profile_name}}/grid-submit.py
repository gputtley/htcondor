#!/usr/bin/env python3

import sys
import re
import htcondor
from os import makedirs
from os.path import join
from uuid import uuid4

from snakemake.utils import read_job_properties

jobscript = sys.argv[1]
job_properties = read_job_properties(jobscript)

UUID = uuid4()  # random UUID
jobDir = "{{cookiecutter.htcondor_log_dir}}/{}_{}".format(job_properties["jobid"], UUID)
makedirs(jobDir, exist_ok=True)

sub_dict = {
    "executable": "/bin/bash",
    "arguments": jobscript,
    "max_retries": "1",
    "log": join(jobDir, "condor.log"),
    "output": join(jobDir, "condor.out"),
    "error": join(jobDir, "condor.err"),
    "getenv": "True",
}

if "params" in job_properties.keys():
    if "submit_options" in job_properties["params"].keys():
        for val in job_properties["params"]["submit_options"]:
            sub_dict[val.split("=")[0]] = val.split("=")[1]


sub = htcondor.Submit(sub_dict)


schedd = htcondor.Schedd()
clusterID = schedd.submit(sub)

# print jobid for use in Snakemake
print("{}_{}_{}".format(job_properties["jobid"], UUID, clusterID))

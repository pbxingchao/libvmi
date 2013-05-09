#!/usr/bin/env python
"""
PyVMI is a python language wrapper for the LibVMI Library. The LibVMI Library
is an introspection library that simplifies access to memory in a target
virtual machine or in a file containing a dump of a system's physical memory.

Author: Bryan D. Payne (bdpayne@acm.org)

Copyright 2013 Bryan D. Payne

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
import pyvmi
import sys


def get_processes(vmi):
    if vmi['ostype'] == 'Linux':
        current_process = vmi.translate(ksym='init_task')
    elif vmi['ostype'] == 'Windows':
        current_process = vmi.read(ksym='PsInitialSystemProcess')

    list_head = current_process + vmi['tasks_offset']
    next_list_entry = vmi.read(va=list_head)

    while (next_list_entry != list_head):
        yield(current_process)
        current_process = next_list_entry - vmi['tasks_offset']
        next_list_entry = vmi.read(va=next_list_entry)


def get_pid_and_proc(vmi):
    process_structs = get_processes(vmi)
    for struct in process_structs:
        procname = vmi.read(va=struct + vmi['name_offset'], string=True)
        pid = vmi.read(va=struct + vmi['pid_offset'], size=4)
        if (pid < 1<<16):
            yield pid, procname


def main(argv):
    with pyvmi.init(argv[1]) as vmi:
        for pid, procname in get_pid_and_proc(vmi):
            print "[%5d] %s" % (pid, procname)


if __name__ == "__main__":
    main(sys.argv)

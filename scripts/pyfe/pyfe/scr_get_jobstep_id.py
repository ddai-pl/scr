#! /usr/bin/env python3

# scr_get_jobstep_id.py

from pyfe.scr_common import runproc
import re
from pyfe.scr_env import SCR_Env

# This script attempts to get the job step id for the last srun command that 
# was launched. The argument to this script is the PID of the srun command.
# The script first calls squeue to get the job steps for this job.
# It assumes that the highest numbered job step is the right one (meaning the
# last one that was started).
# Then it checks to see if the srun command with PID is still running. The idea
# here is that if the srun command died, then the job step with the highest number
# is for some other srun command and not the one we are looking for. 
# This script returns the job step id on success and -1 on failure.

def scr_get_jobstep_id(scr_env=None):
  #my $pid=$ARGV[0]; # unused
  if scr_env is None:
    scr_env = SCR_Env()
  user = scr_env.conf['user']
  if user is None:
    print('scr_get_jobstep_id: ERROR: Could not determine user ID')
    return None
  jobid = scr_env.getjobid()
  if jobid is None:
    print('scr_get_jobstep_id: ERROR: Could not determine job ID')
    return None
  # get job steps for this user and job, order by decreasing job step
  # so first one should be the one we are looking for
  # -h means print no header, so just the data in this order:
  # STEPID         NAME PARTITION     USER      TIME NODELIST
  argv = ['squeue','-h','-s','-u',user,'-j',jobid,'-S','\"-i\"']
  # my $cmd="squeue -h -s -u $user -j $jobid -S \"-i\"";
  output, returncode = runproc(argv=argv,getstdout=True)
  if returncode != 0:
      return -1
  output = output.split('\n')

  currjobid=None

  for line in output:
    line = line.strip()
    #line = re.sub('^(\s+)','',line)
    # $line=~ s/^\s+//;
    fields = re.split('\s+',line)
    # my @fields = split /\s+/, $line;
    #print ("fields ",join(",",@fields),"\n");
    #my @jobidparts=split /\./, $fields[0];
    jobidparts = fields[0].split('.')
    #print ("jobidparts: ", join(",",@jobidparts),"\n");
    # the first item is the job step id
    # if it is JOBID.0, then it is the allocation ID and we don't want that
    # if it's not 0, then assume it's the one we're looking for
    if jobidparts[1]!='0' and jobidparts[1]!='batch':
      currjobid=fields[0]
      break
  return currjobid

if __name__=='__main__':
  ret = scr_get_jobstep_id()
  if ret is not None:
    print('scr_get_jobstep_id: '+str(ret))


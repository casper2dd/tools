#!/usr/bin/env python
#-*- coding: UTF-8 -*-

import sys
from optparse import OptionParser
import subprocess
import shlex
import tempfile
import signal
import os
import time
import json
import shutil

class DistEexception(Exception):
    #The base distribute exception from which all others should subclass.
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

class FileNotFound(DistEexception):
    pass

class ConnectionFiled(DistEexception):
    pass

class CommandExecutionError(DistEexception):
    pass

class CommandExecutionTimeout(DistEexception):
    pass

class FileTypeError(DistEexception):
    pass



class SubWork(object):
    """
    add timeout support!
    if timeout, we SIGTERM to child process, and not to cause zombie process
    safe!
    """
    def __init__(self): 
        """
        default None
        """
        self._Popen = None
        self._pid = None
        self._return_code = None
        self._cwd = None
        self._start_time = None
        self._msg = ''
        self._mpid = os.getpid()

    def _send_signal(self, pid, sig):
        """
        Send a signal to the process
        """
        os.kill(pid, sig)

    def _terminate(self, pid):
        """
        Terminate the process with SIGTERM
        """
        self._send_signal(pid, signal.SIGTERM)

    def _kill(self, pid):
        """
        Kill the process with SIGKILL
        """
        self._send_signal(pid, signal.SIGKILL)

    def _wait(self, Popen):
        """
        Wait child exit signal
        """
        Popen.wait()

    def _free_child(self, pid, Popen):
        """
        Kill process by pid
        """
        try:
            self._terminate(pid)
            self._kill(pid)
            self._wait(Popen)
        except Exception:
            pass

    def _run(self):
        #Run cmd.
        #Split command string.
        cmd = shlex.split(self._cmd)
        try:
            self._Popen = subprocess.Popen(args=cmd, 
                                          stdout=subprocess.PIPE, 
                                          stderr=subprocess.PIPE, 
                                          cwd=self._cwd)
            self._pid = self._Popen.pid
            self._start_time = time.time()

            info={'Date':time.strftime('%Y-%m-%d-%H:%m'),
                  self._taskid:(self._mpid,self._pid),
                  result:'2'}

            if not os.path.exists('/tmp/cgdoing'):
                os.mkdir('/tmp/cgdoing')
            if not os.path.exists('/tmp/cgdone'):
                os.mkdir('/tmp/cgdone')

            with open('/tmp/cgdoing/%s.pid'%self._taskid,'w+b') as self._fd:
                self._fd.write(json.dumps(info))
            
            while (self._Popen.poll() == None and 
                    (time.time() - self._start_time) < self._timeout):
                time.sleep(1)
        except (OSError, ValueError), e:
            #raise exceptions.CommandExecutionError("Execute Commonand Filed.", e)
            raise
        except Exception:
            raise
            
        # Child is not exit yet.
        if self._Popen.poll() == None: 
            self._free_child(self._pid, self._Popen)
            with open('/tmp/cgdoing/%s.pid'%self._taskid,'r') as self._fd:
                info_json=self._fd.read()
                info=json.loads(info_json)
                info['result'] = '1'
            with open('/tmp/cgdoing/%s.pid'%self._taskid,'w+b') as self._fd:
                self._fd.write(json.dumps(info))
            #Throw the Exception that run command timeout.
            raise exceptions.CommandExecutionTimeout("Command Execution Timeout %ds." % self._timeout)
        else:
            self._return_code = self._Popen.poll()
            with open('/tmp/cgdoing/%s.pid'%self._taskid,'r') as self._fd:
                info_json=self._fd.read()
                info=json.loads(info_json)
                info['result'] = self._return_code
            with open('/tmp/cgdoing/%s.pid'%self._taskid,'w+b') as self._fd:
                self._fd.write(json.dumps(info))

        shutil.move('/tmp/cgdoing/%s.pid'%self._taskid,''/tmp/cgdone/%s.pid'%self._taskid,')

    def start(self,
              cmd, 
              timeout=5*60*60,
              stdin=None,
              stdout=None,
              stderr=None,
              tty=False,
              timestamp=False,
              taskid=''):

        self._cmd = cmd
        self._stdin = stdin
        self._stdout = stdout
        self._stderr = stderr
        self._timeout = timeout
        self._is_tty = tty
        self._timestamp = timestamp
        self._taskid = taskid

        try:
            self._run()
        except Exception:
            raise

def option():
    parser = OptionParser()
    parser.add_option("-t", "--timeout", dest="timeout", metavar="", default="5*60*60")
    parser.add_option("-i", "--taskid", dest="taskid",metavar="")
    parser.add_option("-c", "--cmd", dest="cmd",  metavar="")
    print parser.parse_args()
    return parser.parse_args()
        

    # #Create file handle.
    # def _create_handler(self, filename):
    #     if isinstance(filename, file):
    #         return filename
    #     elif isinstance(filename, basestring):
    #         path = os.path.dirname(filename)
    #         timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
            
    #         if not os.path.exists(path):
    #             os.makedirs(path)
    #         elif os.path.exists(filename) and not os.path.isfile(filename):
    #             backup_name = filename + timestamp
    #             os.rename(filename, backup_name)

    #         fd = open(filename, 'a+b')
    #         return fd
    #     else:
    #         raise "The type of \'filename\' must be \'file\' or \'basestring\'"

if __name__ == '__main__':

    (optionval, args) = option()
    print optionval.timeout
    print optionval.taskid
    print optionval.cmd
 

    sub=SubWork()
    sub.start(optionval.cmd,timeout=optionval.timeout,taskid=optionval.taskid)

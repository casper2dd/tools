#!/usr/bin/python

import sys
import os
import paramiko
import socket
import time
from stat import S_IMODE, S_ISDIR, S_ISREG
from contextlib import contextmanager
#from optparse import OptionParser

class ConnectionException(Exception):

    def __init__(self, host, port):
        # Call the base class constructor with the parameters it needs
        Exception.__init__(self, host, port)
        self.message = 'Could not connect to host:port.  %s:%s'

class WTCallbacks(object):
    '''an object to house the callbacks, used internally

    :ivar flist: list of files currently traversed
    :ivar dlist: list of directories currently traversed
    :ivar ulist: list of unknown entities currently traversed
    '''
    def __init__(self):
        '''set instance vars'''
        self.flist = []
        self.dlist = []
        self.ulist = []

    def file_cb(self, pathname):
        '''called for regular files, appends pathname to .flist

        :param str pathname: file path
        '''
        self.flist.append(pathname)

    def dir_cb(self, pathname):
        '''called for directories, appends pathname to .dlist

        :param str pathname: directory path
        '''
        self.dlist.append(pathname)

    def unk_cb(self, pathname):
        '''called for unknown file types, appends pathname to .ulist

        :param str pathname: unknown entity path
        '''
        self.ulist.append(pathname)


class Connection(object):



  def __init__(self,
                 host,
                 username=None,
                 private_key=None,
                 password=None,
                 port=22,
                 log=False,
                ):
        self._sftp_live = False
        self._sftp = None
        if not username:
            username = os.environ['LOGNAME']

        self._logfile = log
        if log:
            if isinstance(log, bool):
                # Log to a temporary file.
                fhnd, self._logfile = tempfile.mkstemp('.txt', 'ssh-',dir='./')
                os.close(fhnd)  # don't want os file descriptors open
            paramiko.util.log_to_file(self._logfile)

        self._transport_live = False
        try:
          self._transport = paramiko.Transport((host, port))
          self._transport_live = True
        except (AttributeError, socket.gaierror):
          raise ConnectionException(host, port)

        if password is not None:
            # Using Password.
            self._transport.connect(username=username, password=password)
        else:
            # Use Private Key.
            if not private_key:
                # Try to use default key.
                if os.path.exists(os.path.expanduser('~/.ssh/id_rsa')):
                    private_key = '~/.ssh/id_rsa'
                elif os.path.exists(os.path.expanduser('~/.ssh/id_dsa')):
                    private_key = '~/.ssh/id_dsa'
                else:
                    raise CredentialException("You have not specified a "\
                                              "password or key.")
            else:
                # use the paramiko agent key
                prv_key = private_key
            self._transport.connect(username=username, pkey=prv_key)

  def _sftp_connect(self):
        """Establish the SFTP connection."""
        if not self._sftp_live:
            self._sftp = paramiko.SFTPClient.from_transport(self._transport)
            self._sftp_live = True

  def _close(self):
        """Closes the connection and cleans up."""
        # Close SFTP Connection.
        if self._sftp_live:
            self._sftp.close()
            self._sftp_live = False
        # Close the SSH Transport.
        if self._transport_live:
            self._transport.close()
            self._transport_live = False
  def __del__(self):
        """Attempt to clean up if not explicitly closed."""
        self._close()

  @property
  def pwd(self):

    '''return the current working directo
    :returns: (str) current working directo
    '''
    self._sftp_connect()
    return self._sftp.normalize('.')

  def get(self, remotepath, localpath=None, callback=None,
            preserve_mtime=False):
        """Copies a file between the remote host and the local host.

        :param str remotepath: the remote path and filename, source
        :param str localpath:
            the local path and filename to copy, destination. If not specified,
            file is copied to local current working directory
        :param callable callback:
            optional callback function (form: ``func(int, int)``) that accepts
            the bytes transferred so far and the total bytes to be transferred.
        :param bool preserve_mtime:
            *Default: False* - make the modification time(st_mtime) on the
            local file match the time on the remote. (st_atime can differ
            because stat'ing the localfile can/does update it's st_atime)

        :returns: None

        :raises: IOError

        """
        if not localpath:
            localpath = os.path.split(remotepath)[1]

        self._sftp_connect()
        if preserve_mtime:
            sftpattrs = self._sftp.stat(remotepath)

        self._sftp.get(remotepath, localpath, callback=callback)
        if preserve_mtime:
            os.utime(localpath, (sftpattrs.st_atime, sftpattrs.st_mtime))

  def get_d(self, remotedir, localdir, preserve_mtime=False):
        """get the contents of remotedir and write to locadir. (non-recursive)

        :param str remotedir: the remote directory to copy from (source)
        :param str localdir: the local directory to copy to (target)
        :param bool preserve_mtime: *Default: False* -
            preserve modification time on files

        :returns: None

        :raises:
        """
        self._sftp_connect()
        with self.cd(remotedir):
            for sattr in self._sftp.listdir_attr('.'):
                if S_ISREG(sattr.st_mode):
                    rname = sattr.filename
                    self.get(rname, os.path.join(localdir, rname),
                             preserve_mtime=preserve_mtime)

  def get_r(self, remotedir, localdir, preserve_mtime=False):
        """recursively copy remotedir structure to localdir

        :param str remotedir: the remote directory to copy from
        :param str localdir: the local directory to copy to
        :param bool preserve_mtime: *Default: False* -
            preserve modification time on files

        :returns: None

        :raises:

        """
        self._sftp_connect()
        wtcb = WTCallbacks()
        self.walktree(remotedir, wtcb.file_cb, wtcb.dir_cb, wtcb.unk_cb)
        # handle directories we recursed through
        for dname in wtcb.dlist:
            for subdir in path_advance(dname):
                try:
                    os.mkdir(reparent(localdir, subdir))
                    wtcb.dlist.append(subdir)
                except OSError:     # dir exists
                    pass

        for fname in wtcb.flist:
            # they may have told us to start down farther, so we may not have
            # recursed through some, ensure local dir structure matches
            head, _ = os.path.split(fname)
            if head not in wtcb.dlist:
                for subdir in path_advance(head):
                    if subdir not in wtcb.dlist and subdir != '.':
                        os.mkdir(reparent(localdir, subdir))
                        wtcb.dlist.append(subdir)

            self.get(fname,
                     reparent(localdir, fname),
                     preserve_mtime=preserve_mtime
                    )

  def walktree(self, remotepath, fcallback, dcallback, ucallback, recurse=True):
        '''recursively descend, depth first, the directory tree rooted at
        remotepath, calling discreet callback functions for each regular file,
        directory and unknown file type.

        :param str remotepath:
            root of remote directory to descend, use '.' to start at
            :attr:`.pwd`
        :param callable fcallback:
            callback function to invoke for a regular file.
            (form: ``func(str)``)
        :param callable dcallback:
            callback function to invoke for a directory. (form: ``func(str)``)
        :param callable ucallback:
            callback function to invoke for an unknown file type.
            (form: ``func(str)``)
        :param bool recurse: *Default: True* - should it recurse

        :returns: None

        :raises:

        '''
        self._sftp_connect()
        for entry in self._sftp.listdir(remotepath):
            pathname = os.path.join(remotepath, entry)
            mode = self._sftp.stat(pathname).st_mode
            if S_ISDIR(mode):
                # It's a directory, call the dcallback function
                dcallback(pathname)
                if recurse:
                    # now, recurse into it
                    self.walktree(pathname, fcallback, dcallback, ucallback)
            elif S_ISREG(mode):
                # It's a file, call the fcallback function
                fcallback(pathname)
            else:
                # Unknown file type
                ucallback(pathname)



  @contextmanager
  def cd(self, remotepath=None):
        """context manager that can change to a optionally specified remote
        directory and restores the old pwd on exit.

        :param str|None remotepath: *Default: None* -
            remotepath to temporarily make the current directory
        :returns: None
        :raises: IOError, if remote path doesn't exist
        """
        try:
            original_path = self.pwd
            if remotepath is not None:
                self.cwd(remotepath)
            yield
        finally:
            self.cwd(original_path)

  def test(self,remotedir):
    self._sftp_connect()
    
    for sattr in self._sftp.listdir_attr(remotedir):
      print sattr.filename
    print "--------------------------------"
    # for entry in self._sftp.listdir(remotedir):

    #     path=os.path.join(remotedir,entry)
    #     print path
    print self._sftp.stat('./test/bash-4.1.2-15.el6_5.2.i686.rpm').st_mode



def path_advance(thepath, sep=os.sep):
    '''generator to iterate over a file path forwards

    :param str thepath: the path to navigate forwards
    :param str sep: *Default: os.sep* - the path separator to use

    :returns: (iter)able of strings

    '''
    # handle a direct path
    pre = ''
    if thepath[0] == sep:
        pre = sep
    curpath = ''
    parts = thepath.split(sep)
    if pre:
        if parts[0]:
            parts[0] = pre + parts[0]
        else:
            parts[1] = pre + parts[1]
    for part in parts:
        curpath = os.path.join(curpath, part)
        if curpath:
            yield curpath


def path_retreat(thepath, sep=os.sep):
    '''generator to iterate over a file path in reverse

    :param str thepath: the path to retreat over
    :param str sep: *Default: os.sep* - the path separator to use

    :returns: (iter)able of strings

    '''
    pre = ''
    if thepath[0] == sep:
        pre = sep
    parts = thepath.split(sep)
    while parts:
        if os.path.join(*parts):
            yield '%s%s' % (pre, os.path.join(*parts))
        parts = parts[:-1]

def reparent(newparent, oldpath):
    '''when copying or moving a directory structure, you need to re-parent the
    oldpath.  When using os.path.join to calculate this new path, the
    appearance of a / root path at the beginning of oldpath, supplants the
    newparent and we don't want this to happen, so we need to make the oldpath
    root appear as a child of the newparent.

    :param: str newparent: the new parent location for oldpath (target)
    :param str oldpath: the path being adopted by newparent (source)

    :returns: (str) resulting adoptive path
    '''

    if oldpath[0] == os.sep:
        oldpath = '.' + oldpath
    return os.path.join(newparent, oldpath)


def walktree(localpath, fcallback, dcallback, ucallback, recurse=True):
    '''on the local file system, recursively descend, depth first, the
    directory tree rooted at localpath, calling discreet callback functions
    for each regular file, directory and unknown file type.

    :param str localpath:
        root of remote directory to descend, use '.' to start at
        :attr:`.pwd`
    :param callable fcallback:
        callback function to invoke for a regular file.
        (form: ``func(str)``)
    :param callable dcallback:
        callback function to invoke for a directory. (form: ``func(str)``)
    :param callable ucallback:
        callback function to invoke for an unknown file type.
        (form: ``func(str)``)
    :param bool recurse: *Default: True* -  should it recurse

    :returns: None

    :raises: OSError, if localpath doesn't exist

    '''

    for entry in os.listdir(localpath):
        pathname = os.path.join(localpath, entry)
        mode = os.stat(pathname).st_mode
        if S_ISDIR(mode):
            # It's a directory, call the dcallback function
            dcallback(pathname)
            if recurse:
                # now, recurse into it
                walktree(pathname, fcallback, dcallback, ucallback)
        elif S_ISREG(mode):
            # It's a file, call the fcallback function
            fcallback(pathname)
        else:
            # Unknown file type
            ucallback(pathname)
    
a=Connection('10.9.11.41',username='liancheng',password='66110467')
a.get_r('/home/liancheng/git/','/root/sftp/')











#   def __init__(self, host='', usr='', psw='',port='22', log_file='./paramiko.log',mykey='/root/.ssh/id_rsa'):
    
#     self._host = host
#     self._username = usr
#     self._pwd = psw
#     self._log_file = log_file
#     self._pkey = mykey
#     self._port = port



#   def connect(self):
#     try:
#       paramiko.util.log_to_file(log_file)
#       self._t=paramiko.Transport((self._host,self._port))
#       if self._pwd == '':
#         private_key = paramiko.RSAKey.from_private_key_file(self._pkey)
#         self._t.connect(username=self._username,pkey=private_key)
#       else:
#         self._t.connect(username=self._username,password=self._pwd)

#       self._sftp=paramiko.SFTPClient.from_transport(self._t)
#       # return ftp
#     except socket.error,socket.gaierror:
#       print("SFTP is unavailable,please check the host,username,private_key and password!")
#       sys.exit(0)

#   def disconnect(self):
#     try:
#       self._sftp.close()
#       self._t.close()
#     except Exception:
#       print("disconnect unnormal")



#   def upload(self,localFile,remoteFile):

#     f = open(localFile, "rb")
#     if os.path.basename(remoteFile) == '':
#       remoteFile=os.path.join(remoteFile,os.path.basename(localFile))
#     #file_name = os.path.basename(localFile)
#     #print file_name
#     try:
#       print remoteFile
#       self._ftp.storbinary('STOR %s'%remoteFile, f, self._buffer_size)
#       f.close()
#     except ftplib.error_perm:
#       return False


#     # ftp = self._connect()
#     # f = open(filepath, "rb")
#     # file_name = os.path.split(filepath)[-1]
#     # try:
#     #   ftp.storbinary('STOR %s'%file_name, f, self._buffer_size)
#     # except ftplib.error_perm:
#     #   return False
#     # self._disconnect(ftp)
#     # return True

#   def downloadfile(self,localFile,remoteFile):

#     if os.path.basename(localFile) == '':
#       localFile=os.path.join(localFile,os.path.basename(remoteFile))
#     f = open(localFile,"wb")
#     try:
#       self._ftp.retrbinary("RETR %s"%remoteFile, f.write, self._buffer_size)
#       f.close()
#     except ftplib.error_perm:
#       return False


#   def downloadfiles(self,localfolder,remotefolder):

#     try:
#       print self._ftp.nlst(remotefolder)
#       file_list=[]
#       file_list=self._ftp.nlst(remotefolder)
#       if not os.path.exists(localfolder):
#         os.makedirs(localfolder) 
#       for remoteFile in file_list:
#         localFile=os.path.join(localfolder, os.path.basename(remoteFile))
#         self.downloadfile(localFile,remoteFile)
#     # except Exception:
#     except ftplib.error_perm:
#       return False
#     #




#   def find(self,filename,remotefolder):
#     file_list=[]
#     file_list=self._ftp.nlst(remotefolder)
#     for file in file_list:
#       #print os.path.basename(file)
#       if filename in os.path.basename(file):
#         result='yes'
#         break
#       else:
#         result='no'
#     if result=='yes':
#       return True
#     else:
#       return False

#   def dir(self,remotefolder):
#     return self._ftp.dir(remotefolder)





# a=ftp(host='192.168.70.131')
# a.connect()
# # print '-------------test dir----------------'
# # a.dir('pub')
# # print '-------------test find----------------'
# # y=a.find('liancheng','pub')
# # print y
# # n=a.find('casper','pub')
# # print n
# # print '-------------test upload----------------'
# # a.upload('D:\\p.py','/pub/')
# print '-------------test downloadfile----------------'
# a.downloadfile('D:\\test\\','/pub/liancheng.txt')
# print '-------------test downloadfiles----------------'
# a.downloadfiles('D:\\test\\test','/pub')
# a.disconnect()

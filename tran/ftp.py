from __future__ import division
import sys
import os
import ftplib
import socket
import time
#from optparse import OptionParser


class ftp(object):

  def __init__(self, host='', usr='', psw='', log_file=None,buffer_size=1024):
    
    self._host = host
    self._username = usr
    self._pwd = psw
    self._log_file = log_file
    self._buffer_size = buffer_size
    self._sizeWritten = 0.0
    self._totalSize = 0.0
    self._percentComplete = 0



  def connect(self,debug_level=False):
    try:
      self._debug_level=debug_level
      self._ftp = ftplib.FTP(self._host)
      self._ftp.login(self._username,self._pwd)
      if self._debug_level:
        self._ftp.set_debuglevel(2)
      # return ftp
    except socket.error,socket.gaierror:
      print("FTP is unavailable,please check the host,username and password!")
      sys.exit(0)

  def disconnect(self):
    try:
      if self._debug_level:
        self._ftp.set_debuglevel(0)
      self._ftp.quit()
    except Exception:
      print("disconnect unnormal")



  def upload(self,localFile,remoteFile):

    f = open(localFile, "rb")
    # if os.path.basename(remoteFile) == '':
    #   remoteFile=os.path.join(remoteFile,os.path.basename(localFile))
    # try:
    #   self._ftp.storbinary('STOR %s'%remoteFile, f, self._buffer_size)
    #   f.close()
    # except ftplib.error_perm:
    #   return False
    if  remoteFile != '' and remoteFile != './':
        if not self.find_folder(remoteFile):
            self.mkd(remoteFile)
    try:
        remoteFile=os.path.join(remoteFile,os.path.basename(localFile))
        totalsize = os.path.getsize(localFile)
        uploadTracker = FtpUploadTracker(int(totalsize))
        self._ftp.storbinary('STOR %s'%remoteFile, f, self._buffer_size,uploadTracker.handle)
        f.close()
    except ftplib.error_perm:
        return False





    # ftp = self._connect()
    # f = open(filepath, "rb")
    # file_name = os.path.split(filepath)[-1]
    # try:
    #   ftp.storbinary('STOR %s'%file_name, f, self._buffer_size)
    # except ftplib.error_perm:
    #   return False
    # self._disconnect(ftp)
    # return True

  def downloadfile(self,localFile,remoteFile):

    # if os.path.isfile(remoteFile):
    #   print "file %s is already exists"%os.path.basename(remoteFile)
    # if not os.path.isdir(os.path.dirname(remoteFile)):
    #   os.makedirs(os.path.dirname(remoteFile))
    # if os.path.basename(localFile) == '':
    #   localFile=os.path.join(localFile, remoteFile)
    # f = open(localFile,"wb")
    # try:
    #   self._ftp.retrbinary("RETR %s"%remoteFile, f.write, self._buffer_size)
    #   f.close()
    # except ftplib.error_perm:
    #   return False
    totalsize = self._ftp.size(remoteFile)

    if os.path.basename(localFile) == '':
      localFile=os.path.join(localFile, remoteFile)
    if not os.path.isdir(os.path.dirname(localFile)):
      os.makedirs(os.path.dirname(localFile))
    f = open(localFile,"wb")
    try:
      downloadTracker = FtpDownloadTracker(int(totalsize),f)
      self._ftp.retrbinary("RETR %s"%remoteFile, downloadTracker.handle, self._buffer_size)
    except ftplib.error_perm:
      return False
    finally:
      f.close()


  def downloadfolder(self,localfolder,remotefolder):

    try:
      print self._ftp.nlst(remotefolder)
      file_list=[]
      file_list=self._ftp.nlst(remotefolder)
      if not os.path.exists(localfolder):
        os.makedirs(localfolder) 
      for remoteFile in file_list:
        #localFile=os.path.join(localfolder, os.path.basename(remoteFile))
        #self.downloadfile(localFile,remoteFile)
        self.downloadfile(localfolder,remoteFile)
    # except Exception:
    except ftplib.error_perm:
      return False
    #




  def find_file(self,filename,remotefolder):
    file_list=[]
    file_list=self._ftp.nlst(remotefolder)
    if file_list:
        for file in file_list:
          #print os.path.basename(file)
          if filename in os.path.basename(file):
            result = 'yes'
            break
          else:
            result = 'no'
        if result == 'yes':
          return True
        else:
          return False
    else:
      return False

  def find_folder(self,remotefolder):
    file_list=[]
    remotefolder = self.format_folder(remotefolder)
    file_list=self._ftp.nlst(os.path.dirname(remotefolder))
    if file_list:
        
        if remotefolder in file_list:
            return True
        else:
            return False
    else:
        return False


  def dir(self,remotefolder):
    return self._ftp.dir(remotefolder)

  def list(self,remotefolder):
    return self._ftp.nlst(remotefolder)

  def mkd(self,remotefolder):
    self._ftp.mkd(remotefolder)

  def format_folder(self,upload_folder):
    if upload_folder.endswith('/'):
        upload_folder=upload_folder[0:-1]
        return upload_folder
    else:
        return upload_folder

class FtpUploadTracker(object):
    sizeWritten = 0
    totalSize = 0
    lastShownPercent = 0

    def __init__(self, totalSize):
        self.totalSize = totalSize

    def handle(self, block):
        self.sizeWritten += 1024
        percentComplete = round((self.sizeWritten / self.totalSize) * 100)
        # print '---------lastShownPercent---------',self.lastShownPercent
        # print '*********percentComplete**********',percentComplete
        if (self.lastShownPercent != percentComplete):
            self.lastShownPercent = percentComplete
            print(str(percentComplete) + " percent complete")

class FtpDownloadTracker(object):
    sizeWritten = 0
    totalSize = 0
    lastShownPercent = 0

    def __init__(self, totalSize,f):
        self.totalSize = totalSize
        self.f = f

    def handle(self, block):
        # f = open(self.filename, "ab")
        self.f.write(block)
        self.f.flush()
        # f.close()
        self.sizeWritten += 1024
        percentComplete = round((self.sizeWritten / self.totalSize) * 100)
        if (self.lastShownPercent != percentComplete):
            self.lastShownPercent = percentComplete           
            print(str(percentComplete) + " percent complete")



#/upload/123123123123/test.txt


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

a=ftp(host='192.168.70.131',usr='liancheng',psw='66110467')
a.connect()
# a.upload('E:\\Tools\\sogou_pinyin_78h.exe','./')
# a.dir('')
a.downloadfile('E:\\','./sogou_pinyin_78h.exe')
# b = a.list('upload/1288/')
# print b
# c = a.find_folder('test/')
# print c
# if b:  37157568  
#   print 'already'
# else:
#   print 'mkdir'
  #a.mkd('upload/1288/')
#c = a.find('123','upload/')
#print c
a.disconnect()


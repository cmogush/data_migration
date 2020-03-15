#testingGit
xDir = r'V:/'
tDir = r"F:\VirtualDrives\share"
targetDirectory = "F:\VirtualDrives\share"

def statusFileCreate():
    statusFile = os.path.join(targetDirectory, "transfer_status.csv")
    if not os.path.exists(statusFile):
        print("create the statusFile")
        with open(statusFile, 'w', newline='') as csvFile:
            header = ['file', 'type', 'status']
            writer = csv.writer(csvFile)
            writer.writerow(header)
        print("statusFile created")


def updateStatus(filename, filetype, updatedStatus):  # update the status value, using the file as a key
    statusFile = os.path.join(targetDirectory, "transfer_status.csv")
    tempfile = os.path.join(targetDirectory, "temp.csv")
    fields = ['file', 'type', 'status']

    with open(statusFile, 'r', newline='') as csvReadFile, open(tempfile, 'w', newline='') as csvWriteFile:
        found = False
        reader = csv.DictReader(csvReadFile, fieldnames=fields)
        writer = csv.DictWriter(csvWriteFile, fieldnames=fields)
        for row in reader:
            if row['file'] == str(filename):
                row['status'] = updatedStatus
                print("found {}...updating status to {}".format(filename, updatedStatus))
                found = True
            row = {'file': row['file'], 'type': row['type'], 'status': row['status']}
            writer.writerow(row)
    if not found:
        print("could not find {}, adding to log as {}".format(filename, updatedStatus))
        with open(tempfile, 'a', newline='') as csvWriteFile:
            writer = csv.DictWriter(csvWriteFile, fieldnames=fields)
            row = {'file': filename, 'type' : filetype, 'status': updatedStatus}
            writer.writerow(row)
    shutil.move(tempfile, statusFile)

def fileAlreadyTransferred(file):
    #print("checking if exists: {}".format(file))
    if os.path.exists(file):
        print("already transferred {}".format(file))
        return True
    print("not transferred: {}".format(file))
    return False

def fileInLog(file): #check and see if there is a status value, using the file as a key
    statusFile = os.path.join(targetDirectory,"transfer_status.csv")
    with open(statusFile) as csvFile:
        reader = csv.DictReader(csvFile)
        for row in reader:
            if row['file'] == file:
                return True
        #print("could not find {}".format(file))
        return False

def getStatus(file): #return the status value, using the file as a key
    statusFile = os.path.join(targetDirectory,"transfer_status.csv")
    with open(statusFile) as csvFile:
        reader = csv.DictReader(csvFile)
        for row in reader:
            if row['file'] == file:
                return row['status']
    #print("could not find {}".format(file))
    return False

def getNewStatus(currStatus):
    if getStatus(currStatus) == "done":
        return True
    elif getStatus(currStatus) == "failed":
        return "failed 2"
    elif getStatus(currStatus) == "failed 2":
        return "cannot xfer"
    return getStatus(currStatus)

def okToSkip(currObj): #check the object status, first see if it exists in the log, if exists and done then return True, if failed return return currStatus
    if fileInLog(currObj):
        print("{} found...skipping".format(currObj))
        currStatus = getStatus(currObj)
        if currStatus == "done" or currStatus == "cannot xfer":
            return True
    print("could not find {}".format(currObj))
    return False

def xferDir(parentDir, dir, parentFolder, folder):
    print(dir)
    print(os.listdir(dir))
    targetFolder = os.path.join(parentFolder, folder)
    if not os.path.isdir(targetFolder):
        os.mkdir(targetFolder)
    for entry in os.listdir(dir):
        try:
            e = os.path.splitext(entry)
            fileExt = e[1]
            if fileExt == "":
                fileExt = "folder"
            currObj = os.path.join(dir,entry)
            if okToSkip(currObj):
                continue
            if fileExt == "folder":
                xfer(dir, currObj, targetFolder, entry)
                updateStatus(currObj, fileExt, 'done')
            else:
                #transfer the file
                original = os.path.join(dir, entry)
                target = os.path.join(targetFolder, entry)
                print("transferring {} to {}".format(original, target))
                shutil.copy(original, target)
                updateStatus(currObj, fileExt, "done")
        except:
            if fileAlreadyTransferred(target):
                updateStatus(currObj, fileExt, "done") #this is important because it will fail if it's already been xferred, just needs to be logged
            else:
                if fileInLog(currObj):
                    updateStatus(currObj, fileExt, getNewStatus(getStatus(currObj))) #if file not xferred and in log already, update the status
                else:
                    updateStatus(currObj, fileExt, "failed") #else add it to the log
            # attempt += 1
            # print("attempt #{}".format(attempt))
            # time.sleep(1)

import os
import shutil
import subprocess
import time
import csv

statusFileCreate()
xferDir("", xDir, targetDirectory, "")
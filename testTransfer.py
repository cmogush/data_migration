originalDirectory = r"C:\Users\cmogush\Desktop\Current Projects\Transfer of Virtual Drives\xfer"
targetDirectory = r"C:\Users\cmogush\Desktop\Current Projects\Transfer of Virtual Drives\tdir"

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
        print("could not find {}, adding to log with status".format(filename, updateStatus()))
        with open(tempfile, 'a', newline='') as csvWriteFile:
            writer = csv.DictWriter(csvWriteFile, fieldnames=fields)
            row = {'file': filename, 'type' : filetype, 'status': updatedStatus}
            writer.writerow(row)
    shutil.move(tempfile, statusFile)

def okToSkip(currObj): #check the object status, first see if it exists in the log, if exists and done then return True, if failed return return currStatus
    if fileInLog(currObj):
        currStatus = getStatus(currObj)
        if currStatus == "done" or currStatus == "cannot xfer":
            #print("{} found...skipping".format(currObj))
            return True
    #print("could not find in log {}".format(currObj))
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

def xferDir(parentDir, dir, parentFolder, folder):
    #print(dir)
    print(os.listdir(dir))
    targetFolder = os.path.join(parentFolder, folder)
    if not os.path.isdir(targetFolder): #if the folder doesn't exist in the target directory, create it
        print("creating directory {}".format(targetFolder))
        os.mkdir(targetFolder)
        print("cycling over directory {}".format(dir))
    for entry in os.listdir(dir):
        try:
            # early exit
            currObj = os.path.join(dir,entry)
            if okToSkip(currObj):
                continue
            #determine file extension
            e = os.path.splitext(entry)
            fileExt = e[1]
            if fileExt == "":
                fileExt = "folder"
            print("current object is {}".format(currObj))
            print("filetype is {}".format(fileExt))
            #if currObj is a folder, begin recursive iteration
            print("dir: "+dir) #dir is the dirname sans sub-foldername
            print("currObj: "+currObj) #currObj is the full dir name including sub-foldername
            print("entry: "+entry) #entry is just the sub-foldername by itself
            print("target folder: "+targetFolder) #targetfolder is the current folder
            if fileExt == "folder":
                print("recursive xfer {}".format(currObj))
                xfer(dir, currObj, targetFolder, entry)
                updateStatus(currObj, fileExt, 'done')
            #if not a folder, transfer the file
            else:
                original = os.path.join(dir, entry)
                target = os.path.join(targetFolder, entry)
                print("transferring {} to {}".format(original, target))
                shutil.copy(original, target)
                updateStatus(currObj, fileExt, "done")
        except:
            print("error")
    #         if fileAlreadyTransferred(target):
    #             updateStatus(currObj, fileExt, "done") #this is important because it will fail if it's already been xferred, just needs to be logged
    #         else:
    #             if fileInLog(currObj):
    #                 updateStatus(currObj, fileExt, getNewStatus(getStatus(currObj))) #if file not xferred and in log already, update the status
    #             else:
    #                 updateStatus(currObj, fileExt, "failed") #else add it to the log

import csv
import os
import shutil
import subprocess

def main():
    statusFileCreate()
    #updateStatus("testfile", "filetype", "updatedStatus")
    # updateStatus("testfile", "filetype", "newStatus")
    xferDir("", originalDirectory, targetDirectory, "")

main()
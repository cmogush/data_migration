#Script to transfer files from a (virtual) directory to another directory

import os
import csv
import time
import random
import shutil
import tempfile
from urllib.request import urlopen
from datetime import datetime

def checkConnection():
    #first establish that there is an internet connection, if not then pause script
    while not internetOn():
        print("Disconnected from internet, trying again in: ")
        for x in range (0,30):
            print(str(30 - x)+" seconds")
            time.sleep(1)

def fileSizeMatches(filesize_final, filesize_original):
    if filesize_final == filesize_original:
        return True
    return False

def internetOn(): #function to see if the internet is on
    listOfUrls = ["http://yahoo.com", "http://msn.com", "http://microsoft.com", "http://apple.com", "http://canon.com",
                  "http://disney.com", "http://netflix.com", "http://youtube.com", "http://twitter.com", "http://wikipedia.com"]
    siteToCheck = str(listOfUrls[random.randint(0,9)])
    print(siteToCheck)
    try:
        urlopen(siteToCheck, timeout=10)
        return True
    except:
        return False

def createTransferCSV(transferCSV, listOfTransfers):
    keys = ['name', 'original', 'target', 'filetype', 'filesize', 'status']
    with open(transferCSV, "w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=keys)
        writer.writeheader()  # will create first line based on keys
        for row in listOfTransfers: # turns the dictionaries into csv
            try:
                writer.writerow(row)
            except:
                print("could not write: " + str(row))

def getFileType(entry):
    e = os.path.splitext(entry)
    fileType = e[1]
    if fileType == "":
        fileType = "folder"
    return fileType

def mapTransfer(originalDir, targetDir, transferList):
    #iterate over all entries in directory
    for entry in os.listdir(originalDir):  # iterate over the original dir
        try:
            #entry = entry.replace(os.sep, '/')
            originalEntry = os.path.join(originalDir, entry)
            targetEntry = os.path.join(targetDir, entry)
            print("adding to map: " + originalEntry)
            fileType = getFileType(entry)  # split it to determine the file type
            fileSize = os.path.getsize(originalEntry) # get the filesize for verification purposes
            # append the dir/entry to the a dictionary entry with 'file type' matching the ext and 'status' : none
            transferList.append({"name": str(entry), "original": str(originalEntry), "target": str(targetEntry),
                                 "filetype": str(fileType), "filesize" : str(fileSize), "status": "awaiting transfer"})
            # if the entry is a folder, add it to the call mapTransfer
            if fileType == "folder":
                mapTransfer(originalEntry, targetEntry, transferList)
        except:
            checkConnection()
            failedLog = os.path.join(targetDir, 'failed.txt')
            with open(failedLog, 'a') as file:
                file.write(str(originalEntry + "\n"))
            continue

def transfer(name, original, target, originalSize, filetype):
    # elif see if the file has already been transfered
    if os.path.exists(target):
        targetFilesize = os.path.getsize(target)  # get the filesize for verification purposes
        if fileSizeMatches(str(originalSize), str(targetFilesize)):  # if it matches then write the row
            print("already transferred | {}".format(name))
            return 'done'
        elif filetype == "folder":
            return 'incomplete'
    # else try to Transfer
    # if it's a folder, create the directory
    if filetype == 'folder':
        os.makedirs(str(target))
        return 'done'
    # else attempt to transfer from 'original' to 'target'
    else:
        print("attempting transfer | {}".format(name))
        shutil.copyfile(str(original), str(target))
        # verify that the filesize matches
        filesize = os.path.getsize(target)
        if fileSizeMatches(str(originalSize), str(filesize)):  # if it matches then write the row
            print("succesfully transffered | {}".format(name))
            return 'done'
        else:
            return 'failed'

def transferFiles(transferCSV, transferDir, retryFailed):
    #iterate over rows on csv
    errors = []
    tempCSVFile = os.path.join(transferDir, "temp.csv")
    #simulatenously create new (temp) csv that will overwrite current csv
    with open(transferCSV, newline='') as csv_file, open(tempCSVFile, 'w', newline='') as temp_csv:
        reader = csv.DictReader(csv_file)
        finishedLog = csv.DictWriter(temp_csv, fieldnames=['name', 'original', 'target', 'filetype', 'filesize', 'status'])
        finishedLog.writeheader()  # will create first line based on keys
        for row in reader:
            #setup temp row
            tempRow = {'name' : row['name'], 'original' : row['original'], 'target' : row['target'],
                'filetype' : row['filetype'], 'filesize' : row['filesize'], 'status' : row['status']}
            #check the status of the entry
            #if it's done, marked skip, or failed = False -first- add row to temp csv -then- continue to next entry
            if not retryFailed and ['status'] == 'failed' or row['status'] == "done":
                print("skipping: {} | status: {}".format(row['name'], row['status']))
                finishedLog.writerow(row)  # write row to temp file
                continue

            #transfer the files
            try:
                tempRow['status'] = transfer(str(row['name']), str(row['original']),
                                         str(row['target']), str(row['filesize']), str(row['filetype']))

            except(IOError, os.error) as why:
                errors.append((row['original'], str(why)))
                #except - add row to temp csv with 'failed' as status
                tempRow['status'] = 'failed'
                print("FAILED | {}".format(row['name']))
            finishedLog.writerow(tempRow)
    #overwrite old csv with new csv
    shutil.move(tempCSVFile, transferCSV)
    if errors:
        for err in errors:
            print(err)

def readLog(transferCSV):
    count = {"total" : 0, "done" : 0, "failed": 0}
    with open(transferCSV, 'r',) as CSVlog:
        log = csv.DictReader(CSVlog)
        for row in log:
            count['total'] += 1
            if row['status'] == "done":
                count["done"] += 1
            if row['status'] == "failed":
                count['failed'] +=1
    return count

def main(map, transfer):
    startTime = datetime.now()
    transferList = []
    originalDir = r'V:/'
    transferDir = r'F:/VirtualDrives/share'
    transferCSV = os.path.join(transferDir, "transferLog.csv")
    if map:
        mapTransfer(originalDir, transferDir, transferList)
        print("{} dir entries added to map...".format(len(transferList)))
        createTransferCSV(transferCSV, transferList)
    if transfer:
        transferFiles(transferCSV, transferDir, retryFailed=True)
        print("file transfer finished...results written to log")
        count = readLog(transferCSV)
        print("------------------------------------------")
        print(str(round(count['done']/count['total']*100)) + "% transferred")
        print("{} files attempted | {} completed successfully | {} failed".format(count['total'], count['done'], count['failed']))
    endTime = datetime.now() - startTime
    print("time elapsed: {}".format(endTime))

main(map=True, transfer=True)
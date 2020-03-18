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
            # print("DEBUG {}".format(row['name']))
            #setup temp row
            tempRow = {'name' : row['name'], 'original' : row['original'], 'target' : row['target'],
                'filetype' : row['filetype'], 'filesize' : row['filesize'], 'status' : row['status']}
            #check the status of the entry
            #if it's done, marked skip, or failed = False -first- add row to temp csv -then- continue to next entry
            # print("DEBUG: Status "+row['status'])
            if not retryFailed and ['status'] == 'failed' or row['status'] == "done":
                print("DEBUG: {} is {}".format(row['name'], row['status']))
                finishedLog.writerow(row)  # write row to temp file
                continue

            #elif see if the file has already been transfered
            if os.path.exists(row['target']):
                fileSize = os.path.getsize(row['target'])  # get the filesize for verification purposes
                if fileSizeMatches(row['filesize'], str(fileSize)): #if it matches then write the row
                    tempRow['status'] = 'done'
                    # print("DEBUG: writing to finished log: {}".format(tempRow))
                    finishedLog.writerow(tempRow)
                    continue
            #else try to Transfer
            try:
                print("trying {}".format(row['name']))
                #if it's a folder, create the directory
                if row['filetype'] == 'folder':
                    os.makedirs(row['target'])
                    tempRow['status'] = 'done'
                    finishedLog.writerow(tempRow)
                #else attempt to transfer from 'original' to 'target'
                else:
                    print("attempting transfer of {}".format(row['name']))
                    shutil.copyfile(row['original'], row['target'])
                    #verify that the filesize matches
                    fileSize = os.path.getsize(row['target'])
                    if fileSizeMatches(row['filesize'], str(fileSize)):  # if it matches then write the row
                        tempRow['status'] = 'done'
                        #add row to temp csv with status as done
                        finishedLog.writerow(tempRow)
                    else:
                        tempRow['status'] = 'failed'
                        finishedLog.writerow(tempRow)
                    # print("DEBUG: writing {} as ".format(tempRow['name'], tempRow['status']))
            except (IOError, os.error) as why:
                errors.append((srcname, dstname, str(why)))
                #except - add row to temp csv with 'failed' as status
                tempRow['status'] = 'failed'
                finishedLog.writerow(tempRow)
                # print("DEBUG: FAILED {}".format(tempRow['name']))
    #overwrite old csv with new csv
    shutil.move(tempCSVFile, transferCSV)

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


def main():
    startTime = datetime.now()
    transferList = []
    originalDir = r'C:\Users\Chris\Desktop\Current Projects\data_migration\test\original'
    transferDir = r"C:\Users\Chris\Desktop\Current Projects\data_migration\test\target"
    transferCSV = os.path.join(transferDir, "transferLog.csv")
    mapTransfer(originalDir, transferDir, transferList)
    print("{} dir entries added to map...".format(len(transferList)))
    createTransferCSV(transferCSV, transferList)
    print("transfer mapped to transferLog.csv")
    transferFiles(transferCSV, transferDir, retryFailed=False)
    print("file transfer finished...results written to log")
    count = readLog(transferCSV)
    print("------------------------------------------")
    print("{} files attempted | {} completed successfully | {} failed".format(count['total'], count['done'], count['failed']))
    endTime = datetime.now() - startTime
    print("time elapsed: {}".format(endTime))


main()
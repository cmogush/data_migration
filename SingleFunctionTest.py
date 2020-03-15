import os
import csv
import time
import random
from urllib.request import urlopen
from datetime import datetime

def checkConnection():
    #first establish that there is an internet connection, if not then pause script
    while not internetOn():
        print("Disconnected from internet, trying again in: ")
        for x in range (0,30):
            print(str(30 - x)+" seconds")
            time.sleep(1)

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

def createTransferCSV(transferDir, listOfTransfers):
    keys = ['name', 'original', 'target', 'filetype', 'filesize', 'status']
    transferCSV = os.path.join(transferDir, "transferLog.csv")
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
    #first establish that there is an internet connection, if not then pause script
    while not internetOn():
        print("Disconnected from internet, trying again in: ")
        for x in range (0,10):
            print(str(10 - x)+" seconds")
            time.sleep(1)
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
            continue

def transferFiles(transferLog, failed):
    #iterate over rows on csv
    #simulatenously create new (temp) csv that will overwrite current csv
    #check the status of the entry
    #if it's done, marked skip, or failed = False -first- add row to temp csv -then- continue to next entry
    #else try to Transfer
        #if it's a folder, create the directory
        #else attempt to transfer from 'original' to 'target'
        #add row to temp csv with status as done
    #except - add row to temp csv with 'failed' as status
    #overwrite old csv with new csv
    return null

def main():
    checkConnection()
    # startTime = datetime.now()
    # transferList = []
    # originalDir = r"C:\Users\cmogush\Desktop\Current Projects\Transfer of Virtual Drives\xfer"
    # transferDir = r"C:\Users\cmogush\Desktop\Current Projects\Transfer of Virtual Drives\tdir"
    # mapTransfer(originalDir, transferDir, transferList)
    # endTime = datetime.now() - startTime
    # print("{} dir entries added to map...time elapsed: {}".format(len(transferList), endTime))
    # createTransferCSV(transferDir, transferList)
    # print("transferLog.csv created")
    # transferLog = r"C:\Users\cmogush\Desktop\Current Projects\Transfer of Virtual Drives\tdir\transferLog.csv"
    # transferFiles(transferLog, failed="False")
    # print("transfer mapped to transferLog.csv")

main()
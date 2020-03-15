def fileAlreadyTransferred(file):
    print("checking if exists: " + file)
    if os.path.exists(file):
        print(file+": already exists")
        return True
    print("not found: "+ file)
    return False

import os
import shutil
import subprocess
import time
currDir =r'V:/'
targetDir = r"F:/VirtualDrives/share"
transfer_log = os.path.join(targetDir, "transfer_log.txt")
for entry in os.listdir(currDir):
    with open(transfer_log, 'a') as log:
        try:
            original = os.path.join(currDir, entry)
            target = os.path.join(targetDir, entry)
            if fileAlreadyTransferred(target):
                 continue
            print("starting transfer of: " + str(entry) + "...")
            shutil.copytree(original, target)
            log.write('\n'+entry+": transferred sucessfully")
        except:
            log.write('\n' + entry + ": failed")
            print(entry+": failed to transfer")

# def transferFiles(cd, td):
#     checkfile(cd, td)
#     original = os.path.join(cd, entry)
#     target = os.path.join(td, entry)
#     shutil.copytree(original, target)



# with os.scandir('.') as it:
#     for entry in it:
#         original = os.path.join(currDir+"\\", entry)
#         target = os.path.join(targetDir, entry)
#         shutil.copyfile(original, target)
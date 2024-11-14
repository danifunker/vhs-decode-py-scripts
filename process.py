#!/usr/bin/env python3
import os
import pathlib
from subprocess import run

directory="."
def mainMenu(selectedFile, associatedFileNames):
    print(f"Working with {selectedFile}:")
    print(f"[1] Compress all u8 files to FLAC in folder {doesFLACExist(associatedFileNames)}")
    print(f"[2] vhs-decode with Video8 {doesTBCExist(associatedFileNames)}")
    print(f"[3] vhs-decode with VHS {doesTBCExist(associatedFileNames)}")
    print(f"[4] ld-analyse to set NTSC black and white levels")
    print(f"[5] Align Audio {doesAlignedAudioExist(associatedFileNames)}")
    print(f"[6] Export to MKV {doesMKVExist(associatedFileNames)}")
    print(f"[7] Rename Source Files")
    print(f"[8] Cleanup files after export, including .u8 if FLAC exists ")
    print(f"[9] Select a different file")
    print(f"[10] Open MKV file {doesMKVExist(associatedFileNames)}")
    print(f"[0] Exit the Program")

def fileMenu(fileList):
    print("Please select a file index:")
    for file in (fileList):
        print(f"[{fileList.index(file)}] {file}")
    fileOption=int(input("Select File: "))
    return fileList[fileOption]

def getFileList(fileType,directory):
    files=[]
    for x in os.listdir(directory):
        if x.endswith(fileType):
            files.append(x)
    files_sorted=sorted(files)
    return files_sorted

def getFilenamePrefix(fileName):
    position=fileName.find("-rf-video-")
    prefix=fileName[0:position]
    return prefix

def getAssociatedFiles(prefix,directory):
    files=[]
    for x in os.listdir(directory):
        if x.startswith(prefix):
            files.append(x)
    return files

def doesTBCExist(associatedFiles):
    if ".tbc.json" in str(associatedFiles):
        return "\x1b[32m ✓ \x1b[39m"
    else:
        return ""

def doesFLACExist(associatedFiles):
    if ".flac" in str(associatedFiles):
        return "\x1b[32m ✓ \x1b[39m"
    else:
        return ""

def doesAlignedAudioExist(associatedFiles):
    if "_aligned.wav" in str(associatedFiles):
        return "\x1b[32m ✓ \x1b[39m"
    else:
        return ""

def doesMKVExist(associatedFiles):
    if ".mkv" in str(associatedFiles):
        return "\x1b[32m ✓ \x1b[39m"
    else:
        return ""

def doesu8Exist(associatedFiles):
    if ".u8" in str(associatedFiles):
        return ""
    else:
        return "\x1b[32m ✓ \x1b[39m"

###Execution functions

def LaunchVHSDecode(selectedFile,format):
    #Need the prefix
    # for file in associatedFiles:
    #     if file.find("-rf-video-40msps.flac") or file.find("-rf-video-40msps.u8"):
    #         videoFile=file
    #         break
    prefix=getFilenamePrefix(selectedFile)
    run(f"vhs-decode --ntsc --tape_speed sp --threads 8 --tape_format {format} --recheck_phase -f 40 {selectedFile} {prefix}-video",shell=True)

def launchLDAnalyze(associatedFiles):
    for file in associatedFiles:
        if file.endswith(".tbc.json"):
            tbcfile=file.replace(".json","")
    if 'tbcfile' in locals():
        run(f"ld-analyse {tbcfile}", shell=True)
    else:
        print("Could not find a tbc.json file. Please run vhs-decode first")

def launchPlayer(associatedFiles):
    for file in associatedFiles:
        if file.endswith(".mkv"):
            mkvFile=file
    if 'mkvFile' in locals():
        run(f"open {mkvFile}", shell=True)
    else:
        print("Could not find an mkv file. Please run Export to MKV first.")
    return associatedFiles

def launchVhsAutoAlign(associatedFiles):
    for file in associatedFiles:
        if file.endswith(".tbc.json"):
            tbcfile=file
    if 'tbcfile' in locals():
        pass
    else:
        print("Could not find a tbc.json file. Please run vhs-decode first")
    for file in associatedFiles:
        if file.endswith("linear-audio-46875sps-3ch-24bit-le.wav"):
            sourceWavFile=file
            destWavFile=file.replace(".wav","_aligned.wav")
    if 'sourceWavFile' in locals():
        pass
    else:
        print(f"Could not find a linear audio file. Does the file exist? {associatedFiles}")
    if 'sourceWavFile' in locals() and 'tbcfile' in locals():
        run(f"ffmpeg -i {sourceWavFile} -filter 'channelmap=map=FL-FL|FR-FR' -f s24le -ac 2 - | mono ~/vhs-decode-auto-audio-align_1.0.0/VhsDecodeAutoAudioAlign.exe stream-align --sample-size-bytes 6 --stream-sample-rate-hz 46875 --json {tbcfile} --rf-video-sample-rate-hz 40000000 | ffmpeg -f s24le -ar 46875 -ac 2 -i - -af aresample=48000 -sample_fmt s16 {destWavFile}",shell=True)

def launchtbcVideoExport(associatedFiles):
    for file in associatedFiles:
        if file.endswith(".tbc.json"):
            tbcfile=file.replace(".json","")
    if 'tbcfile' in locals():
        pass
    else:
        print("Could not find a tbc.json file. Please run vhs-decode first")
    for file in associatedFiles:
        if file.endswith("linear-audio-46875sps-3ch-24bit-le_aligned.wav"):
            alignedWavFile=file
    if 'alignedWavFile' in locals():
        pass
    else:
        print(f"Could not find aligned audio file. Be sure to launch Align Audio prior to this.")
    if 'alignedWavFile' in locals() and 'tbcfile' in locals():
        run(f"tbc-video-export --audio-track {alignedWavFile} {tbcfile}", shell=True)

def launchFlacEncoder():
    run("find . -iname '*.u8' -exec flac --best --sample-rate=40000 --sign=unsigned --channels=1 --endian=little --bps=8 {} \;", shell=True)

def cleanupFiles(associatedFiles, prefix):
    #Does FLAC exist? If so, delete u8
    #Does MKV exist? If so, delete the supporting tbc files
    #Does aligned audio exist? If so delete it 
    if ".flac" in str(associatedFiles) and ".u8" in str(associatedFiles):
        print("Removing .u8 file since FLAC exists")
        for file in associatedFiles:
            if file.endswith(".u8"):
                os.remove(file)
                associatedFiles=getAssociatedFiles(prefix,directory)
    if ".mkv" in str(associatedFiles):
        for file in associatedFiles:
            if file.endswith(".tbc") or file.endswith('.tbc.json') or file.endswith('.tbc.json.bup'):
                print(f"Removing {file}...")
                os.remove(file)
                associatedFiles=getAssociatedFiles(prefix,directory)
    if '_aligned.wav' in str(associatedFiles) and 'linear-audio-46875sps-3ch-24bit-le.wav' in str(associatedFiles):
        for file in associatedFiles:
            if file.endswith('_aligned.wav'):
                print(f"Removing {file}...")
                os.remove(file)
                associatedFiles=getAssociatedFiles(prefix,directory)
        
def renameSourceFiles(associatedFiles, prefix):
    newPrefix = str(input("Enter new prefix filename: "))
    for file in associatedFiles:
        print(f"Changing file {file} to {file.replace(prefix,newPrefix)}")
        os.rename(file,file.replace(prefix,newPrefix))
    selectedFile=fileMenu(showFileList())
    return selectedFile

def showFileList():
    if len(getFileList(".u8", directory)) == 0 or (len(getFileList(".flac", directory)) == len(getFileList(".u8", directory))):
        print("All Files are already converted to FLAC in this folder")
        return(getFileList(".flac", directory))
    else:
        return(getFileList(".u8", directory))

selectedFile=fileMenu(showFileList())
prefix=getFilenamePrefix(selectedFile)
associatedFiles=getAssociatedFiles(prefix,directory)
mainMenu(selectedFile,associatedFiles)
option = int(input("Enter Option: "))

while option != 0:
    match option:
        case 1: 
            launchFlacEncoder()
        case 2: 
            LaunchVHSDecode(selectedFile,"VIDEO8")
        case 3: 
            LaunchVHSDecode(selectedFile,"VHS")
        case 4: 
            launchLDAnalyze(associatedFiles)
        case 5: 
            launchVhsAutoAlign(associatedFiles)
        case 6: 
            launchtbcVideoExport(associatedFiles)
        case 7: 
            selectedFile=renameSourceFiles(associatedFiles, prefix)
        case 8: 
            cleanupFiles(associatedFiles,prefix)
        case 9: 
            selectedFile=fileMenu(showFileList())
        case 10: 
            launchPlayer(associatedFiles)
        case _:
            print("\x1b[31mInvalid Option selected\x1b[39m")
    #Wait for user input so they can review previous output
    input("Review previous output and press enter to continue...")
    #Refresh file list after previous operation
    prefix=getFilenamePrefix(selectedFile)
    associatedFiles=getAssociatedFiles(prefix,directory)
    #Reload the menu
    mainMenu(selectedFile,associatedFiles)
    option = int(input("Enter Option: "))

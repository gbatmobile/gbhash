import hashlib, sys, glob, os, threading, psutil

hashes = {"SHA256": "hashlib.sha256()",
          "MD5": "hashlib.md5()",
          "SHA1": "hashlib.sha1()"}

ALG     = "SHA256"
CPUs    = psutil.cpu_count()
FORCE   = False
OUTFILE = sys.stdout
CHKFILE = None
RECURSIVE = False
VERBOSE = False

BUFLEN  = 16384
DEBUG   = False
VERSION = "v1.1.0-public"

def hashFile(alg, fileName):
    m = eval(hashes[alg])
    try:
        if os.path.getsize(fileName) > 0:
            fd = open (fileName, "rb")

            rBytes = fd.read(BUFLEN)
            while len(rBytes) > 0:
                m.update(rBytes)
                rBytes = fd.read(BUFLEN)
            fd.close()
            hashValue = m.hexdigest()
        else:
            hashValue = "EMPTY FILE"
            if not CHKFILE:  hashValue = hashValue.ljust(m.digest_size*2)
    except Exception as e:
        hashValue = "ACCESS ERROR"
        if not CHKFILE:  hashValue = hashValue.ljust(m.digest_size*2)
        if VERBOSE: print (f"Error hashing {fileName}: {e}", file=sys.stderr)
    return hashValue

def hashFileWorker(cpu, outFile):
    fileName, alg, hashWanted = getFileToHash()
    while fileName:
        if DEBUG: print (f"Hashing {fileName} on cpu {cpu}")
        hashValue = hashFile(alg, fileName)
        if CHKFILE:
            if hashValue.upper() == hashWanted.upper():
               hashValue = "OK"
            else:
               if "ERROR" not in hashValue: hashValue = "FAILED"
        logHash(alg, hashValue, fileName, outFile)
        fileName, alg, hashWanted = getFileToHash()

def getFileToHash():
    lckFiles.acquire()
    try:
        if CHKFILE:
            fileName, alg, hashWanted = filesToHash.pop()
        else:
            fileName, alg, hashWanted = filesToHash.pop(), ALG, None
    except:
        fileName, alg, hashWanted = None, None, None
    lckFiles.release()
    return fileName, alg, hashWanted

def logHash (alg, hashValue, fileName, outFile):
    lckOutput.acquire()
    if CHKFILE:
        toShow = f"{hashValue:13s}{alg:13s}{fileName}\n"
    else:
        toShow = f"{hashValue} ?{alg}*{fileName}\n"
    if VERBOSE: print (toShow, end="")
    outFile.write (toShow.encode('utf-8'))
    lckOutput.release()

def enumFilesToHash(baseToHash):
    global filesToHash

    if  os.path.isfile(baseToHash):
        filesToHash.update({baseToHash})
    elif os.path.isdir(baseToHash):
        if os.path.isabs(baseToHash) and not FORCE:
            showMessage ("Hashing absolute path is dangerous. Use --f flag to force.")

        globFolder = baseToHash+("\\**" if RECURSIVE else "")
        filesToHash.update(glob.glob(globFolder+"\\*", recursive=RECURSIVE))
        filesToHash.update(glob.glob(globFolder+"\\.*", recursive=RECURSIVE))
    else:
        pathAndFile = os.path.split(baseToHash)
        if os.path.isdir(pathAndFile[0]):
            globPattern = pathAndFile[0]+("\\**" if RECURSIVE else "")+"\\"+pathAndFile[1]
        else:
            globPattern = baseToHash
        filesToHash.update(glob.glob(globPattern, recursive=RECURSIVE))
    filesToHash = set(filter(lambda f: os.path.isfile(f), filesToHash))

def enumFilesToCheck(checkFDesc, outFile):
    global filesToHash

    for line in checkFDesc:
        line = line.strip()
        if line[0] != ";":
            fields1 = line.split("*")
            fields2 = fields1[0].split(" ?")
            if (len(fields1) == 2) and (len(fields2) == 2):
                fileName = fields1[1]
                hashWanted = fields2[0].strip()
                alg = fields2[1]
                if alg in hashes.keys():
                    filesToHash.add((fileName, alg, hashWanted))
                else:
                    logHash (alg, "HASH UNSUP", fileName, outFile)
            else:
                logHash ("", "LINE ERROR", line, outFile)



def hashAll(outFile, baseToHash=None):
    if CHKFILE:
        enumFilesToCheck(CHKFILE, outFile)
    else:
        enumFilesToHash(baseToHash)

    threads = []
    for cpu in range(CPUs):
        t = threading.Thread(target=hashFileWorker, args=(cpu, outFile))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

def showMessage(msg = None, showHelp = True):
    if (msg):
        print (msg, file=sys.stderr)

    if showHelp:
        print (f"Usage: {sys.argv[0]} [--s] [--f] [-a (sha256 | sha1 | md5)] [-o oufFile] dirOrFileSource ...", file=sys.stderr)
        print (f"       {sys.argv[0]} -c fileHashes", file=sys.stderr)
        print (f"by GALILEU Batista (with Hamilton Pinho support). Nov, 2023 - {VERSION}", file=sys.stderr)
        print (f"\t--h  show this help.", file=sys.stderr)
        print (f"\t--s  single-threaded. Default: multi-threaded", file=sys.stderr)
        print (f"\t--r  recursive. Default: false", file=sys.stderr)
        print (f"\t--v  verbose. Default: false", file=sys.stderr)
        print (f"\t -a  select hash algorithm: sha256, sha1 or md5. Default: {ALG.lower()}", file=sys.stderr)
        print (f"\t--f  force write in output file. Default: false", file=sys.stderr)
        print (f"\t -o  outFile. File name to save hashes. Default: stdout", file=sys.stderr)
        print (f"\t -c  fileHashes. File name with hashes to check.", file=sys.stderr)
        sys.exit(1)

def processOptions():
    global ALG, CPUs, FORCE, OUTFILE, CHKFILE, RECURSIVE, VERBOSE

    ind = 1
    if (len(sys.argv) == 3) and (sys.argv[1] == '-c'):
        try:
            CHKFILE = open (sys.argv[2], "r", encoding='utf-8')
        except:
            showMessage (f"Access denied to {sys.argv[ind]}!")
        return ind
    else:
        while ind < len(sys.argv):
            if sys.argv[ind] == '--h':
                showMessage()
            elif sys.argv[ind] == '--s':
                CPUs = 1
            elif sys.argv[ind] == '--f':
                FORCE = True
            elif sys.argv[ind] == '--r':
                RECURSIVE = True
            elif sys.argv[ind] == '--v':
                VERBOSE = True
            elif sys.argv[ind] == '-a':
                ind += 1
                if ind < len(sys.argv):
                    ALG = sys.argv[ind].upper()
                    if ALG not in hashes.keys():
                        showMessage (f"Hash algorithm '{sys.argv[ind]}' not supported!")
                else:
                    showMessage ("Hash algorithm not specified.")
            elif sys.argv[ind] == '-o':
                ind += 1
                if ind < len(sys.argv):
                    if FORCE or not os.path.exists(sys.argv[ind]):
                        try:
                            OUTFILE = open (sys.argv[ind], "wb")
                        except:
                            showMessage (f"Access denied to {sys.argv[ind]}!")
                            exit(2)
                    else:
                        showMessage (f"{sys.argv[ind]} exists. Use --f flag to force rewrite.")
                else:
                    showMessage ("Output filename not specified.")
            else:
                break
            ind += 1
        return ind

def main():
    ind = processOptions()
    if OUTFILE == sys.stdout: sys.stdout.reconfigure(encoding='utf-8')

    if CHKFILE:
        hashAll(OUTFILE, CHKFILE)
    else:
        if ind < len(sys.argv):
            while ind < len(sys.argv):
                hashAll(OUTFILE, sys.argv[ind])
                ind += 1
            if OUTFILE != sys.stdout: OUTFILE.close()
        else:
            showMessage (showHelp=True)

lckOutput = threading.Lock()
lckFiles = threading.Lock()
filesToHash = set()
main()
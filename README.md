# gbhash

This is an small command-line hashing tool written in Python 3. It was developed to my own use, but I think it has some interesting features so I would like sharing it.

Main features:

>> * Supports commonly used hash algorithms: SHA1, MD5, SHA256;
>> * Supports multithreading. Each thread hashes a file, other file and so on. It uses many threads as CPU cores available in the system;
>> * Handles filenames with eastern characters;
>> * Operates in recursive mode;
>> * Understands wildcards in filenames to hash;
>> * Outputs file in a format compatible with Unix tools, fsum and others;
>> * Checks hashes inside a file generated previously;
 
Others minor features:

>> * Saves hashes directly in file to avoid misinterpretation of chars in console;
>> * Includes all dependences in one binary file (see Releases).


## Usage

> ```gbhash fileName```
>>generates hash for the fileName

> ```gbhash -r dirName```
>> hashes recursively all files in dirName

> ```gbhash --h```
>> Show help

> This is a help message

```
Usage: gbhash [--s] [--f] [-a (sha256 | sha1 | md5)] [-o oufFile] dirOrFileSource ...
       gbhash -c fileHashes
by GALILEU Batista (with Hamilton Pinho support). Aug, 2023 - v1.0.0-public
        --h  show this help.
        --s  single-threaded. Default: multi-threaded
        --r  recursive. Default: false
        --v  verbose. Default: false
         -a  select hash algorithm: sha256, sha1 or md5. Default: sha256
        --f  force write in output file. Default: false
         -o  outFile. File name to save hashes. Default: stdout
         -c  fileHashes. File name with hashes to check.
```

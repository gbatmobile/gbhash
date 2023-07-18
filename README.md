# gbhash

This is an small command-line hashing tool written in Python 3. It was developed to my own use, but I think it has some interesting features so I would like sharing it.

Main features:

* Support hash algorithms commonly used: SHA1, MD5, SHA256;
* Support multithreading. Each thread hashes a file, other file and so on. It uses many threads as CPU cores available in the system;
* Handle filenames with eastern characters;
* Operates in recursive mode;
* Understand wildcards in filenames to hash;
* Output file format compatible with Unix tools, fsum and others;
* Hash files or check hashes inside a file generated previously;
* Some others options to improve performance;
* All dependences included in one binary file.


## Usage

> ```gbhash fileName```
>>generates hash for the fileName

> ```gbhash -r dirName```
>> hashes recursively all files in dirName

> ```gbhash --h```
>> Show help


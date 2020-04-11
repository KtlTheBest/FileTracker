# FileTracker
Hello, you are at the page of the FileTracker project, a third homework assigned to us on CSCI 333 - Computer Networks course. This project is done by Danel Batyrbek and Zhalghas Khassenov.

## Specifications
The FT is a set of two programs: server and a client.

The first important notice is that users should know about the IP of the FT server. The port number also should be known. For fanciness, let the default port be 1234.

When a client connects to a server, first things first, server should send information about files that the client is willing to share (up to 5 files). For simplicity's sake, the client will share everything in the folder it is run from (yes, if you don't specify the folder and don't chroot, you can suply the source code for FT itself).

The information that the client sends is of the form:
```
    <filename, file type (e.g. text, jpg, etc), file size, file last modified date (DD/MM/YY), IP address, port number>.
```

To perform a handshake, the client must send `"HELLO"` and recieve `"HI"`.

If a server doesn't receive any files information, then it won't connect a client to the FT. FT should not respond to a client.

Only accepted peers should be able to use services offered by this system.

When a client wants to download a file with filename "File Name", the client requests the file from FT by sending `"SEARCH" + File Name`.

When a server receives a `"SEARCH"` from a client, it tries to find a file from a hashtable where `key` is a filename and a `value` is a list which contains records of this format: `<file type, file size, file last modified date (DD/MM/YY), IP addresss, port number>`.
* If FT finds the file, it should send `"FOUND"` + the list of records.
* If FT does not find the file, it should send `"NOT FOUND"`.

When the client receives the list from FT, after a choosing a file to download, it should send `"DOWNLOAD"` to the other client.

When B receives the `"DOWNLOAD"`, it should send to the client `"FILE: " + file`.

When the client wants to leave the system, it should notify FT about this so that FT can update the list of online users. A client should send `"BYE"` to do so.

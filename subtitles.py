#!/usr/bin/python

#
# Script to move globally subtitle timing
#

import sys, re

def ts2int(timestamp):
    """transforms 00:03:14,000 to int"""
    fs=(",",":")
    indexes=[]
    pos = 0
 
    for c in timestamp:
        if c in fs:
            indexes.append(pos)
        pos+=1

    timestamp=list(timestamp)

    pos=0 
    for i in indexes:
        i+=pos
        timestamp.pop(i) 
        pos-=1 # we have to lower position as we just popped out an item

    timestamp=int("".join(timestamp))
    return timestamp 

def int2ts(value):
    """transforms int to 01:01:33,900"""
    value=str(value)
    l = len(value)

    if l < 9:
        value = (9-l)*"0" + value
    
    value=list(value)
    value.insert(2, ":")
    value.insert(5, ":")
    value.insert(8, ",")

    return "".join(value)

def get_time_change(value):
    """get_time_change(value) where value is in format +-00:03:14,000"""
    t=1
    ts_change=0

    if value.startswith("-"):
        t=-1
    elif not value.startswith("+"):
        raise Exception("Excpected timestamp change starting with +/- on input")

    ts_change=ts2int(value[1:])
        
    return t*ts_change
 
    # timestamp looks like 00:03:14,000

def get_content(file):

    try:
        file=open(file, "r")
        content=file.readlines()
        file.close()
        return content

    except IOError:
        print ("Failed to open srt file.")
        sys.exit(2) 

def process_content(content, ts):
  
    cnt=content

    i = 0 
    for line in content:
        if re.match("^ *([0-9]{2}:){2}[0-9]{2},[0-9]{3} *--> *([0-9]{2}:){2}[0-9]{2},[0-9]{3}", line):
            # then replace timestamp
            t1,t2=line.split("-->")
            try:
                t1=ts2int(t1.strip()) +ts
                t2=ts2int(t2.strip()) +ts
            except:
                print ("error in process_content: t1 = %s, t2 = %s\n" % (t1,t2))

            cnt[i] = (int2ts(t1) + " --> " + int2ts(t2) + "\n")
        i+=1
    return cnt

def write_content(content, srt_file):
    try:
        file=open(srt_file, "w")
        file.writelines(content)
        file.close()
    except IOError:
        print("Failed to write into %s\n", srt_file)
        sys.exit(3)
        
                
def main():

    if len(sys.argv) != 3:
        print ("Example Usage:\n\t%s file.srt +00:00:00,001" % (sys.argv[0]))
        sys.exit(1)

    srt_file = sys.argv[1]
    ts_change = get_time_change(sys.argv[2])
    content=get_content(srt_file)
    process_content(content, ts_change)
    write_content(content, srt_file)

    
     
if __name__ == "__main__":
    main()
    
    

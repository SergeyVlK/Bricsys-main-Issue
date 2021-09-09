import os

path_in = "origin_files"
path_out = "modified_files"

files = os.listdir(path_in)

for file in files:
    with open(path_in + "//" + file,"r") as f:
        newline=[]
        for word in f.readlines():        
            newline.append(word.replace("\t\t","\t").replace(",","."))
    with open(path_out + "//" + file,"w") as f:
        for line in newline:
            f.writelines(line)



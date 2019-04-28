# -*- coding: utf-8 -*-
from __future__ import print_function
import re
from Definitions import *
currentline=1
def DeNote(data):#预处理，去除注释
    temp = re.findall('//.*?\n',data,flags=re.DOTALL)
    if(len(temp)>0):
        data=data.replace(temp[0],"")
    temp = re.findall('/\*.*?\*/',data,flags=re.DOTALL)
    if(len(temp)>0):
        data=data.replace(temp[0],"")
    return data
def Scan(line):#经行一次扫描，返回得到的token以及剩余的字符串
    max=''
    TargetRegex=regexs[0]
    subindex=0
    match=False
    for regex in regexs:
        result=re.findall(regex,line,flags=re.DOTALL)
        if(len(result)>0):
            result=result[0]
            index=line.find(result)
            if(index!=0):
                continue
            else:
                if(len(result)>len(max)):
                    match=True
                    max=result
                    TargetRegex=regex
    if(match==False):#出错处理
        print(u"不认识的字符："+line[0])
        return {"data":line[0],"regex":"null","remain":line[1:]}
    else:
        return {"data":max,"regex":TargetRegex,"remain":line[subindex+len(max):]}
def ScanLine(line):#对一行进行重复扫描，获得一组token
    tokens=[]
    temp = line.strip().strip('\t')
    origin=temp
    while True:
        if (temp == ""):
            break
        before=temp
        temp = Scan(temp)
        if (temp['regex'] != "null"):
            token = {}
            token['class'] = "T"
            token['name'] = type[regexs.index(temp['regex'])]
            if (Reserved.has_key(temp['data'])):
                token['name'] = Reserved[temp['data']]
            if (op_table.has_key(temp['data'])):
                token['name'] = op_table[temp['data']]
            token['type'] = temp['data']
            token['row'] = currentline
            token['colum'] = origin.find(before)+1
            if (token['name'] == "Inum"):
                token['type'] = int(token['type'])
            if (token['name'] == "Fnum"):
                token['type'] = float(token['type'])
            tokens.append(token)
        temp = temp['remain'].strip().strip('\t')
        if (temp == ""):
            return tokens
    return tokens
def main(path):
    fd=open(path,'r')
    lines=DeNote(fd.read()).split('\n')
    with open(path,'wb')as f:
        for line in lines:
            f.write(line.strip().strip('\t')+'\n')
    tokens=[]
    for line in lines:
        temptokens=ScanLine(line)
        for token in temptokens:
            tokens.append(token)
        global currentline
        currentline+=1
    return tokens
if __name__ == "__main__":
 for token in(main("test.c")):
     print(token)
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
sys.path.append("../../Source/");
import re
from Definitions import *
currentline=1
def RemoveComments(data):#去除注释
    temp = re.findall('//.*?\n',data,flags=re.DOTALL)
    if(len(temp)>0):
        data=data.replace(temp[0],"")
    temp = re.findall('/\*.*?\*/',data,flags=re.DOTALL)
    if(len(temp)>0):
        data=data.replace(temp[0],"")
    return data
def Scan(line):#经行一次扫描，返回得到的token以及剩余的字符串
    max=''
    target_regex=regexs[0]
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
                    target_regex=regex
    if(match==False):#出错处理
        print(u"非法字符："+line[0])
        return {"data":line[0],"regex":"null","remain":line[1:]}
    else:
        return {"data":max,"regex":target_regex,"remain":line[subindex+len(max):]}
def ScanLine(line):#对一行进行重复扫描，获得一组token
    tokens=[]
    result = line.strip().strip('\t')
    origin=result
    while True:
        if (result == ""):
            break
        before=result
        result = Scan(result)
        if (result['regex'] != "null"):
            token = {}
            token['class'] = "T"
            token['row'] = currentline
            token['colum'] = origin.find(before)+1
            token['name'] = type[regexs.index(result['regex'])].upper()
            token['data'] = result['data']
            token['type'] = token['name']
            if (Reserved.has_key(result['data'])):#保留字，对应文法中->不加引号，认定为终结符
                token['name'] = Reserved[result['data']].lower()
                token['type'] = token['name']
            if (token['name']=="operator".upper() or token['name']=="seperator".upper()):
                #操作符或者界符，对应文法中->加引号，认定为终结符
                token['type'] = token['data']
            if (token['name'] == "int" and token['type'] != "int"):
                token['data'] = int(token['data'])
            if (token['name'] == "float" and token['type'] != "float"):
                token['data'] = float(token['data'])
            if token['name'] == "INT" or token['name'] == "FLOAT":
                #整数与浮点数统一
                token['type'] ='number'
            tokens.append(token)
        result = result['remain'].strip().strip('\t')
        if (result == ""):
            return tokens
    return tokens
def main(path):
    temp=''
    fd=open(path,'r')
    lines=RemoveComments(fd.read()).split('\n')
    for line in lines:
        temp+=(line.strip().strip('\t')+'\n')
    temp=temp[:-1]
    with open(path,'wb')as f:
         f.write(temp)
    tokens=[]
    for line in lines:
        temp=ScanLine(line)
        for token in temp:
            tokens.append(token)
        global currentline
        currentline+=1
    return tokens
if __name__ == "__main__":
 for token in(main("test.c")):
     print(token)
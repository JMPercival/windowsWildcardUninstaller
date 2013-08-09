from subprocess import call
from _winreg import *
from sys import argv
from time import sleep
import re
import os

#global vars
uninstallList=[]

def findString(app):
  """find all keys with a certain wildcard name"""
	found=False
	log.write("[+]Looking for app: "+repr(app)+"\n")
	reg=ConnectRegistry(None,HKEY_LOCAL_MACHINE)
	key=OpenKey(reg,r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
	uninstall=None
	#recurse through to find all keys"""
	keyTemp=None
	for x in range(1024):
		try:
			subKeyName=EnumKey(key,x)
		except EnvironmentError:
			pass
			
		#break out of loop if the key names are the same repeated 
		if keyTemp==subKeyName:
			log.write("[+]Key name repeated, closing 32bit loop...\n")
			break
		keyTemp=subKeyName
		
		subKey=OpenKey(key,subKeyName)
		#simply query the keys to find appropriate and append to uninstallList
		try:
			disName=QueryValueEx(subKey,"DisplayName")
			if str(app).lower() in disName[0].lower():
				log.write("[+]Found application name!\n")
				uninstall=QueryValueEx(subKey,"UninstallString")
				if uninstall != None:
					log.write("[+]Found string and returning! String="+repr(uninstall)+"\n")
					found=True
				CloseKey(reg)
				uninstallList.append(uninstall[0])
		except EnvironmentError:
			pass
			
			
	try:
		key64=OpenKey(reg,r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall")
	except WindowsError:
		log.write("[+]This is not a 64bit machine...\n")
		CloseKey(reg)
		return None
		
	keyTemp=None
	for x in range(1024):
		try:
			subKeyName=EnumKey(key64,x)
		except EnvironmentError:
			pass
			
	#break out of loop if the key names are the same repeated 
		if keyTemp==subKeyName:
			log.write("[+]Key name repeated, closing 64bit loop...\n")
			break
		keyTemp=subKeyName
		
		subKey=OpenKey(key64,subKeyName)
		#simply query the keys to find appropriate and append to uninstallList
		try:
			disName=QueryValueEx(subKey,"DisplayName")
			if str(app).lower() in disName[0].lower():
				log.write("[+]Found application name!\n")
				uninstall=QueryValueEx(subKey,"UninstallString")
				if uninstall != None:
					log.write("[+]Found string and returning! String="+repr(uninstall)+"\n")
					found=True
				CloseKey(reg)
				uninstallList.append(uninstall[0])
		except EnvironmentError:
			pass
			
	#close key to end
	if found==False:
		log.write("[+]Could not find the key for:"+app+"\n")	
	CloseKey(reg)
	
def findRe(st):
	s=re.search(r'c:.+exe',st,re.IGNORECASE)
	if s:
		return str(s.group())
	else: return None
	
def checkString(uninstall):
	if uninstall == None:
		log.write("[+]Uninstall String does not hold anything... Forcing termination\n")
		return 'quit'
	else:
		if 'MsiExec.exe' in uninstall:
			striped=uninstall.split('{')
			end=None
			for x in striped:
				if '}' in x:
					end=x
			msiexec='"MsiExec /x{'
			end=msiexec+end
			end+=' /quiet"'
			return end
		else:
			st=findRe(uninstall)
			if st!=None:
				refUninstall=uninstall.replace(st,"")
				end='"'+st+'"+"'+refUninstall+' /s /v/qn"'
				return end
			else:
				log.write("Regex broke "+uninstall+"\n")
				return None


def sortRemove(lis):
	lis.sort()
	refLis=[]
	for x in range(0,len(lis)):
		if lis[x] not in refLis:
			refLis.append(lis[x])
		else:
			log.write("[+] "+lis[x]+" already in Remove List, removing this to stop duplicates...\n")
	return refLis
	
def runUninstall(func):
	log.write('running: os.system('+func+')\n')
	print "running: os.system("+func+")"    ###Used for testing###
	os.system(eval(func))
	sleep(120)
	
def noneFilter(lis):
	newLis=[]
	for x in lis:
		if x !=None:
			newLis.append(x)
	return newLis
		
def removeQuotes(lis):
	end=lis.replace('"','')
	return end
	
	
def main(arg):
	for x in arg:
		findString(x)
	refUninstallLis=sortRemove(uninstallList)
	refUninstallLis=map(removeQuotes, refUninstallLis)
	refUninstallLis=map(checkString,refUninstallLis)
	endUninstallLis=noneFilter(refUninstallLis)
	for x in endUninstallLis:
		runUninstall(x)
	log.close()
		
"""if uninstall != None:
	refUninstall=checkString(uninstall)
	log.write("[+]Uninstall String:"+refUninstall+"\n")
	#call(refUninstall, shell=True)
	log.write("[+]Starting Uninstall and Sleeping 180 Seconds\n")
	#sleep(180)
log.close()
#print "'"+refUninstall+"'"
#refUninstall=['dir','/S','/Q']
#call(refUninstall, shell=True)"""



if __name__=="__main__":
	log=open("remove.log",'w')
	main(argv[1:])












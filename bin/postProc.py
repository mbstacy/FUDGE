#!/usr/bin/python/2.7.1/bin/python
import expergen 
import os,sys,subprocess,shutil
from subprocess import PIPE
import optparse
from optparse import OptionParser
import shlex
import fudgeList
cnt = 0
def postProc():
     #userinput = '/home/a1r/gitlab/fudge/autogen/finalTests/GFDL-ARRMv2-A01P01X01.CM3.xml'
     force = False #default
     usage = "\n############################################################################"
     usage = usage + "\nEg. postProc -i /home/a1r/gitlab/fudge/autogen/finalTests/GFDL-ARRMv2-A01P01X01.CM3.xml"
	
     parser = OptionParser(usage)
     usage = "Eg. postProc -i /home/a1r/gitlab/fudge/autogen/finalTests/GFDL-ARRMv2-A01P01X01.CM3.xml"
     try:
	userinput 
	uinput = userinput
     except:
#	 print "Looks like uinput is not defined with this piece of code. If you passed it as an option, I'll try to use the command-line option with the XML location instead.." 	
	 userinput = "none"	
     parser.add_option("-i", "--file", dest="uinput",help="pass location of XML template", metavar="FILE")
     parser.add_option("-f", "--force",action="store_true",default=False, help="Force override existing output. Default is set to FALSE/no-override")
     parser.add_option("-v", "--vname", dest="vname",help="pass variable name to be post-processed", metavar="VNAME")

     (options, args) = parser.parse_args()
     if userinput == "none":
        print "Looking for XML location taken from command line option.."
        print "Looks like uinput is not defined with this piece of code. If you passed it as an option, I'll try to use the command-line option with the XML location instead.."
     vname = "" 
     for opts,vals in options.__dict__.items():
         	if(opts == 'uinput'):
                	 uinput = vals
                 	 print uinput
		if(opts == 'force'):
			force = vals 
		if(opts == 'vname'):
			vname = vals
			print "Variable to be post-processed: ",vname
     if uinput is None:	
        uinput = userinput
	
     if not os.path.exists(uinput):
                        print "ERROR Invalid XML path.Quitting. Please use -h for help ",uinput
                        sys.exit()
     print "Force override existing output is set to ",force
     #start_time1, start_time2, end_time1, end_time2, varname, hires1,lowres1,hires2,lowres2,strlist,futstart,futend,amip,calendar,esdMethod,expname1,expname2,freq,truth, predictor,rootdir1,rootdir2,dsuffix,region,lats,late,tstamp,lons,lone,yrtot,leaveit,basedire,outdire,futprefix,params,listlos,listfuts,ver = expergen.listVars(uinput,pp=True)
################ get BASEDIR #################
     basedir = os.environ.get('BASEDIR')
     if(basedir is None):
           print "ERROR: BASEDIR environment variable not set"
	   sys.exit(1)
     output_grid,kfold,lone,region,fut_train_start_time,fut_train_end_time,file_j_range,hist_file_start_time,hist_file_end_time,hist_train_start_time,hist_train_end_time,lats,late,lons,late, basedir,method,target_file_start_time,target_file_end_time,target_train_start_time,target_train_end_time,spat_mask,fut_file_start_time,fut_file_end_time,predictor,target,params,outdir,dversion,dexper,target_scenario,target_model,target_freq,hist_scenario,hist_model,hist_freq,fut_scenario,fut_model,fut_freq,hist_pred_dir,fut_pred_dir,target_dir,expconfig,target_time_window,hist_time_window,fut_time_window,tstamp,ds_region,target_ver,auxcustom,qc_switch,qc_varname,qc_type,adjust_out,sbase,pr_opts = expergen.listVars(uinput,basedir=basedir,pp=True) 
     basedire = basedir	
     esdMethod = method
     varname = target 
     grid = spat_mask+"../"+region+".nc"
     region = ds_region
     outrec = outdir.split('_')
     #amip = outrec[0] 
     #fut = outrec[1]
     #print "amip outdir", amip
     #print "fut outdir", fut
     suff = ".nc"
     cond = 1 
     indir = fut_pred_dir 
     freq = fut_freq
     exper_rip = fut_scenario
     scenario = exper_rip.split('_')[0]
     ens = exper_rip.split('_')[1]	
     ver = dversion
     predModel = fut_model 	
     indir = outdir #Our mini op from dscaling is the input to PP  
     ## if vname  contains the word mask, then yes let's set the indir differently  ##
     if(vname is not None):
    	 if "mask" in vname:
		print "The variable you're trying to PP appears to be a mask variable"
        	print "debug..",indir
        	#indir = indir+"../../../../"+vname+"/"+region+"/OneD/"+ver+"/" 
                indir = indir+"/"+target+"_qcmask/"
        	print "indir ",indir 
      #if vname is passed, we assume we PP the target variable
     else: 
        vname = varname 
        print "default target variable chose to be post-processed. Override with a -v varname.", vname
     obsid = "'"+target_model+"."+target_scenario+"."+target_freq+"."+target_ver+"("+target_train_start_time+"-"+target_train_end_time+")"+"'"
     #"OBS_DATA.GRIDDED_OBS.livneh.historical.atmos.day.r0i0p0.v1p2(1961-2005)"
     if (cond == 1):
           			if (os.path.exists(indir)):
                                        exists = checkExists(vname,indir,region,ver,freq,expconfig,exper_rip,predModel,str(fut_train_start_time),str(fut_train_end_time),suff,force)
             				if (exists == False):

           					print "PP Output does not exist already",indir
						cnt = call_ppFudge(basedire,indir,esdMethod,vname,str(expconfig),exper_rip,region,ver,lons,lone,lats,late,grid,freq,str(fut_train_start_time),str(fut_train_end_time),obsid)
						print "call_ppFudge: COMPLETE "
						print "fudgeList invocation: BEGINS"
						slogloc = sbase+"/"+"experiment_info"
						fcmd = "python "+basedir+"/bin/fudgeList.py -i "+uinput+" -o "+slogloc 
						f = subprocess.Popen(fcmd, stdout=subprocess.PIPE, shell=True)
						out, err = f.communicate() 
						#print "fudgeList out", out
						#if err is not None:
						#	print "fudgeList err", err	
						print "Summary Log File: ", slogloc
						slogloc_alt = indir+"../../../../"
						if("mask" in vname): 
                                                	slogloc_alt = indir+"../../../../../"
						print "Copy summary log to ",os.path.abspath(slogloc_alt+"/experiment_info")	
					        shutil.copy2(slogloc, slogloc_alt)
					else:
						sys.exit("ERROR")
           			else:
                			print "ERROR Input directory ",indir," does not exist. Aborting exec. "
                			sys.exit()

def checkExists(var,indir,region,ver,freq,dexper,exper_rip,predictor,start,end,suff,force):
                                        filedire = indir+"/../../../"+region+"/"+ver+"/"
				        if "mask" in var: #spl cases are not great
	                                        filedire = indir+"/../../../../"+region+"/"+ver+"/"
						print "-----Looking for PP output in:", filedire		
                                        filename =var+"_"+freq+"_"+dexper+"_"+exper_rip+"_"+region+"_"+start+"0101"+"-"+end+"1231"+".nc"
#                                        filename =var+"_"+freq+"_"+esdMethod+"_"+dexper+"_"+drip+"_"+region+"_"+predictor+"_"+start+"0101"+"-"+end+"1231"+".nc"

					print "test test",filedire,filename	
                                        if not os.path.exists(filedire+"/"+filename):                
                                           exists = False  
                                        else:
					   if (force == True):	
					   	print "CAUTION : PP output  already exists. But -f is turned on, so output will be overwritten"	
						exists = False
					   else:
						exists = True
						print "ERROR: PP output already exists. ", filedire,"/",filename,". Please use -f option to override this. Quitting now.."
					print filename
				        return exists		

def call_ppFudge(basedire,indir,method,var,dexper,exper_rip,region,ver,lons,lone,lats,late,grid,freq,start,end,obsid):
        script1Loc = basedire+"/utils/pp/ppFudge" #"/main/code/esd/autogen/ppFudge"
	print script1Loc 
#check if output already exists
#options basedir indir method var epoch rip region ver
#TODO rem redundant region to cattool

        fileprefix =var+"_"+freq+"_"+dexper+"_"+exper_rip+"_"+region+"_"+start+"0101"+"-"+end+"1231" 
	cmd =  script1Loc+" "+basedire+" "+indir+" "+method+" "+var+" "+dexper+" "+exper_rip+" "+region+" "+ver+" "+str(lons)+" "+str(lone)+" "+str(lats)+" "+str(late)+" "+str(grid)+" "+fileprefix+" "+obsid
        print "PP ..in progress", cmd 
       	#p = subprocess.Popen('tcsh -c "'+cmd+'"',shell=True,stdout=PIPE,stdin=PIPE, stderr=PIPE)
        p = subprocess.Popen('tcsh -c "'+cmd+'"',shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
	error,output = p.communicate()
	print p.returncode ,output, error
        word = "ERROR"
        if (p.returncode != 0):
         print "!!!! FAILED !!!!,error occured in call_ppFudge. Please save log and contact Aparna Radhakrishnan"
         sys.exit(0)
	if word in error:
         print "!!!! FAILED. !!!!,error occured in call_ppFudge. Please save log and contact Aparna Radhakrishnan"
         sys.exit(0)
         ############################################################################################
        global cnt
	cnt = cnt + 1
        print "1- completed\n"
	return p.returncode
if __name__ == '__main__':
    postProc()

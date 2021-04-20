"""

    Mininet-WiFi: A simple networking testbed for Wireless OpenFlow/SDWN!

author: Ramon Fontes (ramonrf@dca.fee.unicamp.br)

"""



from mininet.log import debug
import time
import sys
import os
import numpy as np
#from randomForestAssociation import pred
#from scipy import stats
#import group_mobility as gm
from mn_wifi.link import wirelessLink, Association

SLOW_MOB = 0
MED_MOB = 1
HIGH_MOB = 2

SHORT_RANGE = 0
LARGE_RANGE = 1

SMALL_TIME = 0
MED_TIME = 1
LONG_TIME = 2


class associationControl(object):
    "Mechanisms that optimize the use of the APs"

    changeAP = False

    global tupSM
    global tupMM
    global tupHM
    tupSM = (SLOW_MOB,0.6)
    tupMM = (MED_MOB,1.8)
    tupHM = (HIGH_MOB,6.0)

    def __init__(self, sta, ap, wlan, ac):
	#print(dir(self))
	#print('{"associationControl":"%s"}\n' %(str(ac)))
        if ac in dir(self):
	    #print('{"associationControl":"%s"}\n' %(str(ac)))
            self.__getattribute__(ac)(sta=sta, ap=ap, wlan=wlan)

    def llf(self, sta, ap, wlan):
        #llf: Least loaded first
        apref = sta.params['associatedTo'][wlan]
        if apref != '':
            ref_llf = len(apref.params['associatedStations'])
            if len(ap.params['associatedStations']) + 2 < ref_llf:
                debug('iw dev %s disconnect\n' % sta.params['wlan'][wlan])
                sta.pexec('iw dev %s disconnect' % sta.params['wlan'][wlan])
                self.changeAP = True
        else:
            self.changeAP = True
        return self.changeAP

#    def ssf(self, sta, ap, wlan):
        #ssf: Strongest signal first
#        distance = sta.get_distance_to(sta.params['associatedTo'][wlan])
#        rssi = sta.set_rssi(sta.params['associatedTo'][wlan], wlan, distance)
#        ref_dist = sta.get_distance_to(ap)
#        ref_rssi = sta.set_rssi(ap, wlan, ref_dist)
#        if float(ref_rssi) > float(rssi + 0.1):
#            debug('iw dev %s disconnect\n' % sta.params['wlan'][wlan])
#            sta.pexec('iw dev %s disconnect' % sta.params['wlan'][wlan])
#            self.changeAP = True
#        return self.changeAP
#value = self.ssf(sta, apAcc, wlan, ap_wlan)

    def ssf(self, sta, ap, wlan):
	#ssf: Strongest signal first
	tiempo_inicial = time.time()
	distance = sta.get_distance_to(sta.params['associatedTo'][wlan])
	rssi = sta.set_rssi(sta.params['associatedTo'][wlan], wlan, distance)
	ref_dist = sta.get_distance_to(ap)
	ref_rssi = sta.set_rssi(ap, wlan, ref_dist)
	aps_inrange = []
	aps_range = []

	for i in range( len(sta.params["apsInRange"]) ):
		ap_temp = sta.params['apsInRange'][i]
		aps_inrange.append(ap_temp.name)
		aps_range = [ap_temp]

	if float(ref_rssi) > float(rssi + 0.1):
		tiempo_final = time.time()
		time_selec = tiempo_final - tiempo_inicial
		debug('iw dev %s disconnect\n' % sta.params['wlan'][wlan])
		sta.pexec('iw dev %s disconnect' % sta.params['wlan'][wlan])
		self.changeAP = True

		nodesL2 = aps_range
                for sw in nodesL2:
                    #print("changeAP HO 3 AP<%s" %sw.name)
                    sw.dpctl('del-flows')
                    sw.cmd('ovs-ofctl del-flows %s' % sw.name)


		print("**************************method execution ssf test **************************")
		f= open("/home/wifi/new3/mininet-wifi/scripts/output/ssf.txt","a+")
		#f.write('{"time":"%s", "sta":"%s", "oldAp":"%s", "newAp":"%s", "apsInRange":"%s", "speed":"%s", "position": "%s"}\n' %(str(tiempo_inicial),str(sta.name),str(sta.params['associatedTo'][wlan]), str(ap.name), str(sta.params['apsInRange']), str(sta.params['speed']), str(sta.params['position'])))

		f.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\n' %(str(tiempo_inicial),str(sta.name),str(sta.params['associatedTo'][wlan]), str(ap.name), str(aps_inrange), str(sta.params['speed']), str(sta.params['position'])))

		f.close()
		print('{"time":"%s", "sta":"%s", "oldAp":"%s", "newAp":"%s", "apsInRange":"%s", "speed":"%s", "position": "%s"}\n' %(str(tiempo_inicial),str(sta.name),str(sta.params['associatedTo'][wlan]), str(ap.name), str(aps_inrange), str(sta.params['speed']), str(sta.params['position'])))
		sta.params['battery'] = sta.params['battery'] - 0.1
		#print("assoc_py node: %s - battery: %s" % (sta.name, str(sta.params['battery'])))
	return self.changeAP

#    def keywithmaxval(d):
#        """ a) create a list of the dict's keys and values; 
#         b) return the key with the max value"""  
#        v=list(d.values())
#        k=list(d.keys())
#        return k[v.index(max(v))]

    def simknowOld(self, sta, ap, wlan): #12 abril 2021
	    #SIMKNOW: Semantic Information Model
	    #print("\n---SIMKNOW---")

        tiempo_inicial = time.time()
        aps_temp = {}
        aps_pref = {}
        aps_disc = {}
        ap_target = sta.params['associatedTo']
	idx_target = 0
        value = False
        userSpeed = SLOW_MOB
        sizeAP = SHORT_RANGE
	aps_inrange = [] 
	aps_range = []   

        speedSta = sta.params['speed']
        if float(speedSta) < tupMM[1]:
		userSpeed = tupSM[0]
        elif (float(speedSta) > tupMM[1]) and (float(speedSta) < tupHM[1]):
		userSpeed = tupMM[0]
        else:
		userSpeed = tupHM[0]
    
        distance = sta.get_distance_to(sta.params['associatedTo'][wlan])
        rssi = sta.set_rssi(sta.params['associatedTo'][wlan], wlan, distance)
        staass = sta.params['associatedTo'][wlan]

	#print(sta.params['apsInRange'])
	#print(sta.params['apsInRange'][0])   

        for i in range( len(sta.params["apsInRange"]) ):
		ap_temp = sta.params['apsInRange'][i]
            	#print(ap_temp)
            	#print(ap_temp.name)
		aps_inrange.append(ap_temp.name)
		aps_range = [ap_temp]
            
          
            	if ap_temp not in sta.params['associatedTo']:
               		#print("ap_asss")
			#print(ap_temp)

                	rangeAp = ap_temp.params['range'][0]
                	if float(rangeAp) < 40:
                    		sizeAP = SHORT_RANGE
                	else:
                    		sizeAP = LARGE_RANGE

                	ref_dist = sta.get_distance_to(ap_temp)
                	ref_rssi = sta.set_rssi(ap_temp, wlan, ref_dist)
        
                	if ((userSpeed == HIGH_MOB) and (sizeAP == SHORT_RANGE)):
                    		sojournTime = SMALL_TIME
				aps_disc[ap_temp] = [ref_rssi, "SMALL_TIME" ]
                	elif ((userSpeed == SLOW_MOB) and (sizeAP == LARGE_RANGE)):
                    		sojournTime = LONG_TIME
				aps_temp[ap_temp] = [ref_rssi, "LONG_TIME"]
                	else:
                    		sojournTime = MED_TIME
				aps_pref[ap_temp] = [ref_rssi, "MED_TIME"]
                
                #if float(ref_rssi) > float(rssi + 0.1):
               		#print("ap_asssRSSI")
			#print(ap_temp)
                    #policies
                	#if (sojournTime == MED_TIME):
                    	#	aps_pref[ap_temp] = [ref_rssi, MED_TIME]
                	#elif (sojournTime == LONG_TIME):
                    	#	aps_temp[ap_temp] = [ref_rssi, LONG_TIME]
                	#else:
                    	#	aps_disc[ap_temp] = [ref_rssi, SMALL_TIME]
 		            
            #dis_to_aptemp = sta.get_distance_to(ap_temp)
            #rangeAp = ap_temp.params['range'][0]
            #if not((float(speedSta) > 3) and (float(rangeAp) < 40)):
                #print (" LongSojournTime")
                #aps_temp.append(ap_temp)
                #else:
                #    print (" SmallSojournTime")
     
            #aps_temp.append(ap_temp.name)

        # if len(aps_pref) > 0:
        #     for apAcc in aps_pref:
        #         if apAcc not in sta.params['associatedTo']:
        #            #ssf: Strongest signal first
        #             ref_dist = sta.get_distance_to(apAcc)
        #             ref_rssi = sta.set_rssi(apAcc, wlan, ref_dist)
        #             if float(ref_rssi) > float(rssi + 0.1):
        #                 aps_cand.append(apAcc)
        #                 rssi_cand.append(ref_rssi)
        
        # if len(aps_temp) > 0:
        #     for apAcc in aps_temp:
        #         if apAcc not in sta.params['associatedTo']:
        #            #ssf: Strongest signal first
        #             ref_dist = sta.get_distance_to(apAcc)
        #             ref_rssi = sta.set_rssi(apAcc, wlan, ref_dist)
        #             if float(ref_rssi) > float(rssi + 0.1):
        #                 aps_cand.append(apAcc)
        #                 rssi_cand.append(ref_rssi)
        
        # numbers = [55, 4, 92, 1, 104, 64, 73, 99, 20]
        # max_value = max(numbers)
        # print('Maximum value:', max_value, "At index:", numbers.index(max_value))
    
	#print("dictionarios")
        #print(aps_pref)
	#print(aps_temp)
    
        if len(aps_pref) > 0:
            	#print("rssi_associated")
	        #print(staass)
	        #print(rssi)
	        #print(aps_cand)
	        #print("rssi_candidatos")
	        #print(rssi_cand)
	        #print(len(aps_cand))
            	#value = True
            	v=list(aps_pref.values())
            	k=list(aps_pref.keys())
            	ap_target = k[v.index(max(v))]
	    	val = aps_pref.get(ap_target)[0]

	    	if float(val) > float(rssi + 0.1):
	    		value = True
	    		#print("ap_targetpref")
	    		#print(aps_pref)
	    		#print(ap_target)
            		#print("apSS_RSSI")
			#print(rssi)

            #ap_target = keywithmaxval(aps_pref)
    
            # for a in range(len(aps_pref)):
            #     if float(rssi_cand[a]) > float(rssi_max + 0.1):
            #         rssi_max = rssi_cand[a]
            #         idx_max = a
            #print("idxmax")
	        #print(aps_cand[idx_max])
        elif len(aps_temp) > 0:
            	#value = True
            	v=list(aps_temp.values())
            	k=list(aps_temp.keys())
            	ap_target = k[v.index(max(v))]
	    	val = aps_temp.get(ap_target)[0]
	    	if float(val) > float(rssi + 0.1):
			value = True
			#print("ap_targetTemp")
	    		#print(aps_temp)
	    		#print(ap_target)
            		#print("apSS_RSSI")
			#print(rssi)
            		#ap_target = keywithmaxval(aps_temp)
        else:
		value = False
    
        if(value == True):
		

		for i in range( len(sta.params["apsInRange"]) ):
			if ap_target == sta.params['apsInRange'][i]:
			    idx_target = i

		debug('iw dev %s disconnect\n' % sta.params['wlan'][wlan])
		sta.pexec('iw dev %s disconnect' % sta.params['wlan'][wlan])
            	Association.associate_infra(sta, sta.params['apsInRange'][idx_target], wlan=wlan, ap_wlan=0)
                nodesL2 = aps_range
                for sw in nodesL2:
                    #print("changeAP HO 3 AP<%s" %sw.name)
                    sw.dpctl('del-flows')
                    sw.cmd('ovs-ofctl del-flows %s' % sw.name)
    
	    	tiempo_final = time.time()
	    	time_selec = tiempo_final - tiempo_inicial
		
	    	#aps_cand = list(aps_pref.keys()) + list(aps_temp.keys())

		print("**************************method execution simknow test **************************")		
	    	print('{"time":"%s", "sta":"%s", "oldAp":"%s", "newAp":"%s", "apsInRange":"%s", "speed":"%s", "position": "%s"}\n' %(str(tiempo_inicial),str(sta.name),str(staass), str(ap_target), str(aps_inrange), str(sta.params['speed']), str(sta.params['position'])))
	    
	    	f= open("/home/wifi/new3/mininet-wifi/scripts/output/simknow.txt","a+")

		f.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\n' %(str(tiempo_inicial),str(sta.name),str(staass), str(ap_target), str(aps_inrange), str(sta.params['speed']), str(sta.params['position'])))
	    
	    	#f.write('{"time":"%s","sta":"%s", "oldAp":"%s", "newAp":"%s", "apsInRange":"%s", "speed":"%s", "position": "%s"}\n' %(str(tiempo_inicial),str(sta.name),str(staass), str(ap_target), str(aps_inrange), str(sta.params['speed']), str(sta.params['position'])))
	    
	    	f.close()
        
        #f.write('{"time_seleccion_grupo":"%s","sta":"%s", "oldAp":"%s", "newAp":"%s", "apsInRange":"%s", "battery":"%s", "position": "%s"}\n' %(str(time_selec*1000),str(disp.name),str(disp.params['associatedTo'][wlan]), str(disp.params['apsInRange'][indice]), str(aps_in_range_name), str(disp.params['battery']), str(disp.params['position'])))

	self.changeAP = value
	return self.changeAP

#////////////////////////////****************************
    def simknow(self, sta, ap, wlan):#12/04/2021
	    #SIMKNOW: Semantic Information Model
	    #print("\n---SIMKNOW---")

        tiempo_inicial = time.time()
        aps_temp = {}
        aps_pref = {}
        aps_disc = {}
        ap_target = sta.params['associatedTo']
	idx_target = 0
        value = False
        userSpeed = SLOW_MOB
        sizeAP = SHORT_RANGE
	aps_inrange = [] 
	aps_range = []   

        speedSta = sta.params['speed']
        if float(speedSta) < tupMM[1]:
		userSpeed = tupSM[0]
        elif (float(speedSta) > tupMM[1]) and (float(speedSta) < tupHM[1]):
		userSpeed = tupMM[0]
        else:
		userSpeed = tupHM[0]
    
        distance = sta.get_distance_to(sta.params['associatedTo'][wlan])
        rssi = sta.set_rssi(sta.params['associatedTo'][wlan], wlan, distance)
        staass = sta.params['associatedTo'][wlan]

	#print(sta.params['apsInRange'])
	#print(sta.params['apsInRange'][0])   

        for i in range( len(sta.params["apsInRange"]) ):
		ap_temp = sta.params['apsInRange'][i]
            	#print(ap_temp)
            	#print(ap_temp.name)
		aps_inrange.append(ap_temp.name)
		aps_range = [ap_temp]

            	#print("ap_asss")
		#print(ap_temp)

                rangeAp = ap_temp.params['range'][0]
                if float(rangeAp) < 40:
                	sizeAP = SHORT_RANGE
                else:
                	sizeAP = LARGE_RANGE

                ref_dist = sta.get_distance_to(ap_temp)
                ref_rssi = sta.set_rssi(ap_temp, wlan, ref_dist)
        
                if ((userSpeed == HIGH_MOB) and (sizeAP == SHORT_RANGE)):
                	sojournTime = SMALL_TIME
			aps_disc[ap_temp] = [ref_rssi, "SMALL_TIME" ]
		elif ((userSpeed == MED_MOB) and (sizeAP == SHORT_RANGE)):
                	sojournTime = MED_TIME
			aps_disc[ap_temp] = [ref_rssi, "SMALL_TIME" ]
                elif ((userSpeed == SLOW_MOB) and (sizeAP == SHORT_RANGE)):
                	sojournTime = LONG_TIME
			aps_temp[ap_temp] = [ref_rssi, "MED_TIME"]
                else:
                	sojournTime = MED_TIME
			aps_pref[ap_temp] = [ref_rssi, "MED_TIME"]

#SLOW_MOB = 0
#MED_MOB = 1
#HIGH_MOB = 2
#SMALL_TIME = 0
#MED_TIME = 1
#LONG_TIME = 2
                
                #if float(ref_rssi) > float(rssi + 0.1):
               		#print("ap_asssRSSI")
			#print(ap_temp)
                    #policies
                	#if (sojournTime == MED_TIME):
                    	#	aps_pref[ap_temp] = [ref_rssi, MED_TIME]
                	#elif (sojournTime == LONG_TIME):
                    	#	aps_temp[ap_temp] = [ref_rssi, LONG_TIME]
                	#else:
                    	#	aps_disc[ap_temp] = [ref_rssi, SMALL_TIME]
 		            
            #dis_to_aptemp = sta.get_distance_to(ap_temp)
            #rangeAp = ap_temp.params['range'][0]
            #if not((float(speedSta) > 3) and (float(rangeAp) < 40)):
                #print (" LongSojournTime")
                #aps_temp.append(ap_temp)
                #else:
                #    print (" SmallSojournTime")
     
            #aps_temp.append(ap_temp.name)

        # if len(aps_pref) > 0:
        #     for apAcc in aps_pref:
        #         if apAcc not in sta.params['associatedTo']:
        #            #ssf: Strongest signal first
        #             ref_dist = sta.get_distance_to(apAcc)
        #             ref_rssi = sta.set_rssi(apAcc, wlan, ref_dist)
        #             if float(ref_rssi) > float(rssi + 0.1):
        #                 aps_cand.append(apAcc)
        #                 rssi_cand.append(ref_rssi)
        
        # if len(aps_temp) > 0:
        #     for apAcc in aps_temp:
        #         if apAcc not in sta.params['associatedTo']:
        #            #ssf: Strongest signal first
        #             ref_dist = sta.get_distance_to(apAcc)
        #             ref_rssi = sta.set_rssi(apAcc, wlan, ref_dist)
        #             if float(ref_rssi) > float(rssi + 0.1):
        #                 aps_cand.append(apAcc)
        #                 rssi_cand.append(ref_rssi)
        
        # numbers = [55, 4, 92, 1, 104, 64, 73, 99, 20]
        # max_value = max(numbers)
        # print('Maximum value:', max_value, "At index:", numbers.index(max_value))
    
	#print("dictionarios")
        #print(aps_pref)
	#print(aps_temp)
    
        if len(aps_pref) > 0:
            	#print("rssi_associated")
	        #print(staass)
	        #print(rssi)
	        #print(aps_cand)
	        #print("rssi_candidatos")
	        #print(rssi_cand)
	        #print(len(aps_cand))
            	#value = True
            	v=list(aps_pref.values())
            	k=list(aps_pref.keys())
            	ap_target = k[v.index(max(v))]
	    	val = aps_pref.get(ap_target)[0]

    		#print("ap_targetpref")
    		#print(aps_pref)
    		#print(ap_target)
		#print(staass)

		if staass != ap_target:

	    	#if float(val) > float(rssi + 0.1):
	    		value = True
	    		#print("ap_targetpref")
	    		#print(aps_pref)
	    		#print(ap_target)
			#print(staass)
            		#print("apSS_RSSI")
			#print(rssi)

            #ap_target = keywithmaxval(aps_pref)
    
            # for a in range(len(aps_pref)):
            #     if float(rssi_cand[a]) > float(rssi_max + 0.1):
            #         rssi_max = rssi_cand[a]
            #         idx_max = a
            #print("idxmax")
	        #print(aps_cand[idx_max])
        elif len(aps_temp) > 0:
            	#value = True
            	v=list(aps_temp.values())
            	k=list(aps_temp.keys())
            	ap_target = k[v.index(max(v))]
	    	val = aps_temp.get(ap_target)[0]

		#print("ap_targetTemp")
    		#print(aps_temp)
    		#print(ap_target)
		#print(staass)

		if staass != ap_target:
	    	#if float(val) > float(rssi + 0.1):
			value = True
			#print("ap_targetTemp")
	    		#print(aps_temp)
	    		#print(ap_target)
			#print(staass)
            		#print("apSS_RSSI")
			#print(rssi)
            		#ap_target = keywithmaxval(aps_temp)
        else:
		value = False
    
        if(value == True):
		

		for i in range( len(sta.params["apsInRange"]) ):
			if ap_target == sta.params['apsInRange'][i]:
			    idx_target = i

		debug('iw dev %s disconnect\n' % sta.params['wlan'][wlan])
		sta.pexec('iw dev %s disconnect' % sta.params['wlan'][wlan])
            	Association.associate_infra(sta, sta.params['apsInRange'][idx_target], wlan=wlan, ap_wlan=0)
                nodesL2 = aps_range
                for sw in nodesL2:
                    #print("changeAP HO 3 AP<%s" %sw.name)
                    sw.dpctl('del-flows')
                    sw.cmd('ovs-ofctl del-flows %s' % sw.name)
    
	    	tiempo_final = time.time()
	    	time_selec = tiempo_final - tiempo_inicial
		
	    	#aps_cand = list(aps_pref.keys()) + list(aps_temp.keys())

		print("**************************method execution simknow test **************************")		
	    	print('{"time":"%s", "sta":"%s", "oldAp":"%s", "newAp":"%s", "apsInRange":"%s", "speed":"%s", "position": "%s"}\n' %(str(tiempo_inicial),str(sta.name),str(staass), str(ap_target), str(aps_inrange), str(sta.params['speed']), str(sta.params['position'])))
	    
	    	f= open("/home/wifi/new3/mininet-wifi/scripts/output/simknow.txt","a+")

		f.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\n' %(str(tiempo_inicial),str(sta.name),str(staass), str(ap_target), str(aps_inrange), str(sta.params['speed']), str(sta.params['position'])))
	    
	    	#f.write('{"time":"%s","sta":"%s", "oldAp":"%s", "newAp":"%s", "apsInRange":"%s", "speed":"%s", "position": "%s"}\n' %(str(tiempo_inicial),str(sta.name),str(staass), str(ap_target), str(aps_inrange), str(sta.params['speed']), str(sta.params['position'])))
	    
	    	f.close()
        
        #f.write('{"time_seleccion_grupo":"%s","sta":"%s", "oldAp":"%s", "newAp":"%s", "apsInRange":"%s", "battery":"%s", "position": "%s"}\n' %(str(time_selec*1000),str(disp.name),str(disp.params['associatedTo'][wlan]), str(disp.params['apsInRange'][indice]), str(aps_in_range_name), str(disp.params['battery']), str(disp.params['position'])))

	self.changeAP = value
	return self.changeAP

#////////////////////////************************************
#*******************************/////////////////////////////////////


    def topsisNew(self, sta, ap, wlan):
	#topsis_VFinal_SIN_Grupos contiene la implementacion final de topsis sin la implementacion de movilidad en grupo
	#TOPSIS: Technique for Order of Preference by Similarity to Ideal Solution (sin movilidad en grupo)
	#print("\n---TOPSIS Normalizacion por costo---")
	#print("\n---TOPSIS SIN GRUPOS---")
	tiempo_inicial = time.time() 
	md = np.array([])						#MATRIZ DE DECISION
	#mp = np.array([ 2./6, 1./6, 3./6])		#VECTOR DE PESOS
	#mp = np.array([ 2./5., 2./5., 1./5.])
	#mp = np.array([ 0.3, 0.5, 0.2])
	#mp = np.array([ 0.5, 0.5, 0.0])
	#mp = np.array([ 1/3, 1/3, 1/3])
	#mp = np.array([ 0.0, 0.0, 1.0])
	#mp = np.array([ 0.2, 0.5, 0.3])
	#mp = np.array([ 0.2974, 0.6167, 0.0859])
	mp = np.array([ 0.33, 0.36, 0.31])
	Alist = [r for r in md]
	aps_temp = []
		
	for i in range( len(sta.params["apsInRange"]) ):
		ap_temp = sta.params['apsInRange'][i]
		rssi_aptemp = sta.set_rssi(ap_temp,0,sta.get_distance_to(ap_temp))
			
		if str(ap_temp.name) == str(sta.params['associatedTo'][wlan]):
			n_est_aptemp = len(ap_temp.params['associatedStations'])
		else:
			n_est_aptemp = len(ap_temp.params['associatedStations']) + 2
			
		dis_to_aptemp = sta.get_distance_to(ap_temp)
			
		#bat_temp = 0.01 * dis_to_aptemp
	
		sta_app = sta.params.get("app", 1)
			
		bat_temp = 0.001 * dis_to_aptemp * sta_app
			
		ocup_aptemp = (n_est_aptemp*100.)/ap_temp.params['maxDis'] # se saca la ocupacion del AP en porcentaje
		newrow = [rssi_aptemp*-1, ocup_aptemp, bat_temp]
		Alist.append(newrow)
		aps_temp.append(ap_temp.name)
		
	md = np.array(Alist)
	m21 = 1./md
	m22 = m21**2
	m23 = m22.sum(axis=0)
	m24 = m23**(0.5)
	mnd = m21/m24
	#matriz normalizada de pesos
	mnp = mnd * mp
	#maximos y minimos de cada columna
	v_max = mnp.max(axis=0)
	v_min = mnp.min(axis=0)
	#Calcular la separacion de la SOLUCION IDEAL POSITIVA Y NEGATIVA (PIS)(NIS) 
	#PIS
	m41 = mnp - v_max
	m42 = m41**2
	m_pis = m42.sum(axis=1)**(0.5) 

	#NIS
	m412 = mnp - v_min
	m422 = m412**2
	m_nis = m422.sum(axis=1)**(0.5) 
		
	m_sep = np.array([m_pis,m_nis])		#MATRIZ de separacion a la SOLUCION IDEAL
		
	# cercania relativa a la solucion ideal
	m51 = m_sep.sum(axis=0)
	
	v_cer = m_sep[1,0:]/m51
	if str(sta.params['associatedTo'][wlan]) != aps_temp[v_cer.argmax()]:
		tiempo_final = time.time()
		time_selec = tiempo_final - tiempo_inicial
		f= open("/home/wifi/new3/mininet-wifi/scripts/output/topsisk.txt","a+")
		f.write('{"time":"%s", "sta":"%s", "oldAp":"%s", "newAp":"%s", "apsInRange":"%s", "speed":"%s", "position": "%s"}\n' %(str(tiempo_inicial),str(sta.name),str(sta.params['associatedTo'][wlan]), str(aps_temp[v_cer.argmax()]), str(aps_temp), str(sta.params['speed']), str(sta.params['position'])))
		f.close()
                print('{"time":"%s", "sta":"%s", "oldAp":"%s", "newAp":"%s", "apsInRange":"%s", "speed":"%s", "position": "%s"}\n' %(str(tiempo_inicial),str(sta.name),str(sta.params['associatedTo'][wlan]), str(aps_temp[v_cer.argmax()]), str(aps_temp), str(sta.params['speed']), str(sta.params['position'])))
		debug('iw dev %s disconnect\n' % sta.params['wlan'][wlan])
		sta.pexec('iw dev %s disconnect' % sta.params['wlan'][wlan])
		Association.associate_infra(sta, sta.params['apsInRange'][v_cer.argmax()], wlan=wlan, ap_wlan=0)
		self.changeAP = True
		sta.params['battery'] = sta.params['battery'] - 0.1
		#sta.params['battery'] = sta.params['battery'] - (0.01 * sta.get_distance_to(sta.params['associatedTo'][wlan]))
		#print("assoc_py node: %s - battery: %s" % (sta.name, str(sta.params['battery'])))
		
	else:
		self.changeAP = False
			
	return self.changeAP

	#topsis_VFinal_SIN_Grupos def topsis(self, sta, ap, wlan, ap_wlan):
    def topsis(self, sta, ap, wlan):
		#topsis_VFinal_SIN_Grupos contiene la implementacion final de topsis sin la implementacion de movilidad en grupo
		#TOPSIS: Technique for Order of Preference by Similarity to Ideal Solution (sin movilidad en grupo)
		#print("\n---TOPSIS Normalizacion por costo---")
		#print("\n---TOPSIS SIN GRUPOS---")
		tiempo_inicial = time.time() 
		md = np.array([])						#MATRIZ DE DECISION
		#mp = np.array([ 2./6, 1./6, 3./6])		#VECTOR DE PESOS
		#mp = np.array([ 2./5., 2./5., 1./5.])
		#mp = np.array([ 0.3, 0.5, 0.2])
		#mp = np.array([ 0.5, 0.5, 0.0])
		#mp = np.array([ 1/3, 1/3, 1/3])
		#mp = np.array([ 0.0, 0.0, 1.0])
		#mp = np.array([ 0.2, 0.5, 0.3])
		#mp = np.array([ 0.2974, 0.6167, 0.0859])
		mp = np.array([ 0.33, 0.36, 0.31])
		Alist = [r for r in md]
		aps_temp = []
		aps_range = [] 
		
		for i in range( len(sta.params["apsInRange"]) ):
			ap_temp = sta.params['apsInRange'][i]
			aps_range = [ap_temp]
			#rssi_aptemp = sta.get_rssi(ap_temp,0,sta.get_distance_to(ap_temp))
			rssi_aptemp = sta.set_rssi(ap_temp,0,sta.get_distance_to(ap_temp))
			
			if str(ap_temp.name) == str(sta.params['associatedTo'][wlan]):
				n_est_aptemp = len(ap_temp.params['associatedStations'])
			else:
				n_est_aptemp = len(ap_temp.params['associatedStations']) + 2
			
			dis_to_aptemp = sta.get_distance_to(ap_temp)
			
			#bat_temp = 0.01 * dis_to_aptemp
			
			sta_app = sta.params.get("app", 1)
			
			bat_temp = 0.001 * dis_to_aptemp * sta_app
			
			#--print("ap: " + str(ap_temp.name) + " distancia: " + str(dis_to_aptemp) + " app: " + str(sta_app) + " bat_temp" + str(bat_temp))
			
			#n_est_aptemp = len(ap_temp.params['associatedStations'])
			#dis_to_aptemp = sta.get_distance_to(ap_temp)
			"""
			print ("AP name %s" %ap_temp.name )
			print ("RSSI %s" %str(rssi_aptemp) )
			print ("# estations %s" %str(n_est_aptemp) )
			print ("Distance to AP %s" %str(dis_to_aptemp) )
			"""
			#newrow = [ap_temp.name, rssi_aptemp, n_est_aptemp, dis_to_aptemp]
			#newrow = [rssi_aptemp, n_est_aptemp*-1, dis_to_aptemp*1000]
			#newrow = [rssi_aptemp, n_est_aptemp*-1, dis_to_aptemp*-1]
			
			ocup_aptemp = (n_est_aptemp*100.)/ap_temp.params['maxDis'] # se saca la ocupacion del AP en porcentaje
			#print("num_sta: " + str(n_est_aptemp)+ " - max_disp: " + str(ap_temp.params['maxDis']) +  " - ocupacion: " + str(ocup_aptemp))
			#newrow = [rssi_aptemp*-1, n_est_aptemp, bat_temp]
			newrow = [rssi_aptemp*-1, ocup_aptemp, bat_temp]
			Alist.append(newrow)
			aps_temp.append(ap_temp.name)
		
		md = np.array(Alist)
		"""
		print(aps_temp)
		print(md)
		print(mp)
		"""
		
		"""
		md12 = md**2
		md13 = md12.sum(axis=0)**(0.5)	#divisor de cada columna
		
		#matriz normalizada de decision
		mnd = md/md13
		"""
		
		m21 = 1./md
		
		m22 = m21**2
		
		m23 = m22.sum(axis=0)
		
		m24 = m23**(0.5)
		
		mnd = m21/m24
		
		#matriz normalizada de pesos
		mnp = mnd * mp
		
		#maximos y minimos de cada columna
		v_max = mnp.max(axis=0)
		v_min = mnp.min(axis=0)
		
		#Calcular la separacion de la SOLUCION IDEAL POSITIVA Y NEGATIVA (PIS)(NIS) 
		
		#PIS
		m41 = mnp - v_max
		m42 = m41**2
		m_pis = m42.sum(axis=1)**(0.5) 

		#NIS
		m412 = mnp - v_min
		m422 = m412**2
		m_nis = m422.sum(axis=1)**(0.5) 
		
		
		m_sep = np.array([m_pis,m_nis])		#MATRIZ de separacion a la SOLUCION IDEAL
		
		# cercania relativa a la solucion ideal
		m51 = m_sep.sum(axis=0)
		
		v_cer = m_sep[1,0:]/m51
		"""
		print('vector de cercanias')
		print(v_cer)
		#mejor red
		print('mejor red')
		print(v_cer.max())
		#Posicion del argumento maximo
		print('posicion de la mejor red')
		print(v_cer.argmax())
		"""
		"""
		f_prueba= open("/home/mininet/Escritorio/scripts/output/topsis_prueba.txt","a+")
		f_prueba.write("%s\n" %md)
		f_prueba.close()
		
		f_prueba2= open("/home/mininet/Escritorio/scripts/output/topsis_prueba2.txt","a+")
		f_prueba2.write("%s %s %s %s\n" %(str(sta.name), aps_temp, str(sta.params['associatedTo'][wlan]), str(sta.params['position'])))
		f_prueba2.close()
		"""
		staass = sta.params['associatedTo'][wlan]
		if str(sta.params['associatedTo'][wlan]) != aps_temp[v_cer.argmax()]:
			tiempo_final = time.time()
			time_selec = tiempo_final - tiempo_inicial
			
			debug('iw dev %s disconnect\n' % sta.params['wlan'][wlan])
			sta.pexec('iw dev %s disconnect' % sta.params['wlan'][wlan])
			Association.associate_infra(sta, sta.params['apsInRange'][v_cer.argmax()], wlan=wlan, ap_wlan=0)
			sta.params['battery'] = sta.params['battery'] - 0.1
			self.changeAP = True

			nodesL2 = aps_range
                	for sw in nodesL2:
                    		#print("changeAP HO 3 AP<%s" %sw.name)
                    		sw.dpctl('del-flows')
                    		sw.cmd('ovs-ofctl del-flows %s' % sw.name)

			print('{"time":"%s", "sta":"%s", "oldAp":"%s", "newAp":"%s", "apsInRange":"%s", "speed":"%s", "position": "%s"}\n' %(str(tiempo_inicial),str(sta.name),str(staass), str(aps_temp[v_cer.argmax()]), str(aps_temp), str(sta.params['speed']), str(sta.params['position'])))

			f= open("/home/wifi/new3/mininet-wifi/scripts/output/topsis.txt","a+")
			#f= open("/home/mininet/Escritorio/scripts/output/topsis.txt","a+")
			print('diferente red')
			print("**************************method execution**************************")
			"""
			print('\n---------------------------------------')
			print('Old AP: ' + str(sta.params['associatedTo'][wlan]))
			print('New AP: ' + str(sta.params['apsInRange'][v_cer.argmax()].name))
			print('New AP2: ' + str(aps_temp[v_cer.argmax()]))
			print('New AP: ' + str(sta.params['apsInRange']))
			"""
			#f.write('\n\n---------------------------------------')
			#f.write('\nOld AP: ' + str(sta.params['associatedTo'][wlan]))
			#f.write('\nNew AP: ' + str(aps_temp[v_cer.argmax()]))
			#f.write('\nAps in Range: ' + str(sta.params['apsInRange']))
			#f.write("{}, {}, {}\n".format(str(sta.params['associatedTo'][wlan]), str(aps_temp[v_cer.argmax()]), str(aps_temp)))
			#f.write("oldAp:'%s', newAp:'%s', apsInRange:'%s'\n" %(str(sta.params['associatedTo'][wlan]), str(aps_temp[v_cer.argmax()]), str(aps_temp)))
			#print('{"time":"%s", "sta":"%s", "oldAp":"%s", "newAp":"%s", "apsInRange":"%s", "battery":"%s", "position": "%s"}\n' %(str(time_selec*1000),str(sta.name),str(sta.params['associatedTo'][wlan]), str(aps_temp[v_cer.argmax()]), str(aps_temp), str(sta.params['battery']), str(sta.params['position'])))

			f.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\n' %(str(tiempo_inicial),str(sta.name),str(staass), str(aps_temp[v_cer.argmax()]), str(aps_temp), str(sta.params['speed']), str(sta.params['position'])))

			#f.write('{"time":"%s", "sta":"%s", "oldAp":"%s", "newAp":"%s", "apsInRange":"%s", "speed":"%s", "position": "%s"}\n' %(str(tiempo_inicial),str(sta.name),str(sta.params['associatedTo'][wlan]), str(aps_temp[v_cer.argmax()]), str(aps_temp), str(sta.params['speed']), str(sta.params['position'])))
		

			#f.write('{"time":"%s", "sta":"%s", "oldAp":"%s", "newAp":"%s", "apsInRange":"%s", "battery":"%s", "position": "%s"}\n' %(str(time_selec*1000),str(sta.name),str(sta.params['associatedTo'][wlan]), str(aps_temp[v_cer.argmax()]), str(aps_temp), str(sta.params['battery']), str(sta.params['position'])))
			#f.write('{"time":"%s", "sta":"%s", "apsInRange":"%s", "battery":"%s", "position": "%s", "oldAp":"%s", "newAp":"%s"}\n' %(str(time_selec*1000),str(sta.name), str(aps_temp), str(sta.params['battery']), str(sta.params['position']), str(sta.params['associatedTo'][wlan]), str(aps_temp[v_cer.argmax()])))
			#f.write(str(sta.params['associatedTo'][wlan]))
			f.close()
		
			#sta.params['battery'] = sta.params['battery'] - (0.01 * sta.get_distance_to(sta.params['associatedTo'][wlan]))
			#print("assoc_py node: %s - battery: %s" % (sta.name, str(sta.params['battery'])))
			
		else:
			#print('misma red')
			self.changeAP = False
			
		return self.changeAP

    def simknow1(self, sta, ap, wlan):
	#SIMKNOW: Semantic Information Model
	print("\n---SIMKNOW---")
	tiempo_inicial = time.time()
	aps_temp = []
	value = False
	userSpeed = SLOW_MOB
	sizeAP = SHORT_RANGE

	speedSta = sta.params['speed']
	if float(speedSta) < tupMM[1]:
		userSpeed = tupSM[0]
	elif (float(speedSta) > tupMM[1]) and (float(speedSta) < tupHM[1]):
		userSpeed = tupMM[0]
	else:
		userSpeed = tupHM[0]

	for i in range( len(sta.params["apsInRange"]) ):
		ap_temp = sta.params['apsInRange'][i]
		#rssi_aptemp = sta.set_rssi(ap_temp,0,sta.get_distance_to(ap_temp))
			
		if str(ap_temp.name) == str(sta.params['associatedTo'][wlan]):
			n_est_aptemp = len(ap_temp.params['associatedStations'])
		else:
			n_est_aptemp = len(ap_temp.params['associatedStations']) + 2

		rangeAp = ap_temp.params['range'][0]
		if float(rangeAp) < 40:
			sizeAP = SHORT_RANGE
		else:
			sizeAP = LARGE_RANGE

		if (userSpeed == HIGH_MOB) and (sizeAP == SHORT_RANGE):
			sojournTime = SMALL_TIME
		elif (userSpeed == SLOW_MOB) and (sizeAP == LARGE_RANGE):
			sojournTime = LONG_TIME
			aps_temp.append(ap_temp)
		else:
			sojournTime = MED_TIME
			aps_temp.append(ap_temp)

		#dis_to_aptemp = sta.get_distance_to(ap_temp)
		#rangeAp = ap_temp.params['range'][0]
		#if not((float(speedSta) > 3) and (float(rangeAp) < 40)):
			#print (" LongSojournTime")
			#aps_temp.append(ap_temp)
			#else:
			#	print (" SmallSojournTime")

	for apAcc in aps_temp:
		if apAcc not in sta.params['associatedTo']:
			value = self.ssf(sta, apAcc, wlan)
			print ("SIMKnowSSF")
			#if value is True:
               		#	nodesL2 = aps_temp
			#	for sw in nodesL2:
            		#			print("changeAP HO 3 AP<%s" %sw.name)
                    	#			sw.dpctl('del-flows')
            		#			#sw.cmd('ovs-ofctl del-flows %s' % sw.name)

		if not sta.params['associatedTo'][wlan] or value:
            		if apAcc not in sta.params['associatedTo']:
                		Association.associate_infra(sta, apAcc, wlan=wlan, ap_wlan=0)
			
	changeAP = value
	return self.changeAP


	def saw(self, sta, ap, wlan, ap_wlan):
		#SAW: Simple Additive Weighting
		print("\n---SAW---")
		tiempo_inicial = time.time() 
		md = np.array([])						#MATRIZ DE DECISION
		#mp = np.array([ 2./6, 1./6, 3./6])		#VECTOR DE PESOS
		#mp = np.array([ 2./5., 2./5., 1./5.])
		#mp = np.array([ 0.4, 0.6])
		mp = np.array([ 0.33, 0.36, 0.31])
		Alist = [r for r in md]
		aps_temp = []
		
		for i in range( len(sta.params["apsInRange"]) ):
			ap_temp = sta.params['apsInRange'][i]
			rssi_aptemp = sta.get_rssi(ap_temp,0,sta.get_distance_to(ap_temp))
			#n_est_aptemp = len(ap_temp.params['associatedStations'])
			dis_to_aptemp = sta.get_distance_to(ap_temp)
			if str(ap_temp.name) == str(sta.params['associatedTo'][wlan]):
				n_est_aptemp = len(ap_temp.params['associatedStations'])
			else:
				n_est_aptemp = len(ap_temp.params['associatedStations']) + 2
			
			dis_to_aptemp = sta.get_distance_to(ap_temp)
			
			sta_app = sta.params.get("app", 1)
			
			bat_temp = 0.001 * dis_to_aptemp * sta_app
			
			print("ap: " + str(ap_temp.name) + " distancia: " + str(dis_to_aptemp) + " app: " + str(sta_app) + " bat_temp" + str(bat_temp))
			
			
			"""
			print ("AP name %s" %ap_temp.name )
			print ("RSSI %s" %str(rssi_aptemp) )
			print ("# estations %s" %str(n_est_aptemp) )
			print ("Distance to AP %s" %str(dis_to_aptemp) )
			"""
			
			#newrow = [ap_temp.name, rssi_aptemp, n_est_aptemp, dis_to_aptemp]
			#newrow = [rssi_aptemp, n_est_aptemp*-1, dis_to_aptemp*1000]
			#newrow = [rssi_aptemp*-1, n_est_aptemp, dis_to_aptemp]
			
			ocup_aptemp = (n_est_aptemp*100.)/ap_temp.params['maxDis'] # se saca la ocupacion del AP en porcentaje
			
			
			print("num_sta: " + str(n_est_aptemp)+ " - max_disp: " + str(ap_temp.params['maxDis']) +  " - ocupacion: " + str(ocup_aptemp))
			#print("application: " + str(sta_app))
			
			newrow = [rssi_aptemp*-1, ocup_aptemp, bat_temp]
			#newrow = [rssi_aptemp*-1, n_est_aptemp, bat_temp]
			Alist.append(newrow)
			aps_temp.append(ap_temp.name)
			n2_est_aptemp = len(ap_temp.params['associatedStations'])
			f= open("/home/mininet/Escritorio/scripts/output/datosML3.txt","a+")
			f.write("{},{},{},{},{},{},{}\n".format(str(sta.name), str(ap_temp.name), str(rssi_aptemp), str(n2_est_aptemp), str(dis_to_aptemp), str(bat_temp), str(sta.params['associatedTo'][wlan])))
			f.close()
		
		md = np.array(Alist)
		"""
		print(aps_temp)
		print(md)
		print(mp)
		"""
		#maximos de cada columna de la matriz de decision
		m2 = md.min(axis=0)
		#print ("max")
		#print m2
		#matriz de decision sobre el vector de maximos
		m3 = m2/md
		#print ("m3")
		#print m3
		
		# multiplicar por el vector de pesos
		m4 = m3 * mp
		#print ("m4")
		#print m4
		
		#suma de las filas (vector de cercanias)
		v_cer = m4.sum(axis=1)
		#print ("m5")
		#print v_cer
		
		#mejor red
		#print ("mejor red puntaje")
		#print(v_cer.max())
		#Posicion del argumento maximo
		#print ("mejor red posicion")
		#print(v_cer.argmax())
		
		
		if str(sta.params['associatedTo'][wlan]) != aps_temp[v_cer.argmax()]:
			tiempo_final = time.time()
			time_selec = tiempo_final - tiempo_inicial
			f= open("/home/mininet/Escritorio/scripts/output/saw.txt","a+")
			"""
			print('diferente red')
			print("**************************method execution**************************")
			print ("aps")
			print(aps_temp)
			print ("matriz decision")
			print(md)
			print ("vector pesos")
			print(mp)
			print ("vector cercanias")
			print v_cer
			print ("mejor red puntaje")
			print(v_cer.max())
			#Posicion del argumento maximo
			print ("mejor red posicion")
			print(v_cer.argmax())
			"""
			
			"""
			print('\n---------------------------------------')
			print('Old AP: ' + str(sta.params['associatedTo'][wlan]))
			print('New AP: ' + str(sta.params['apsInRange'][v_cer.argmax()].name))
			print('New AP2: ' + str(aps_temp[v_cer.argmax()]))
			print('New AP: ' + str(sta.params['apsInRange']))
			"""
			#f.write('\n\n---------------------------------------')
			#f.write('\nOld AP: ' + str(sta.params['associatedTo'][wlan]))
			#f.write('\nNew AP: ' + str(aps_temp[v_cer.argmax()]))
			#f.write('\nAps in Range: ' + str(sta.params['apsInRange']))
			#f.write("{}, {}, {}\n".format(str(sta.params['associatedTo'][wlan]), str(aps_temp[v_cer.argmax()]), str(aps_temp)))
			#f.write("oldAp:'%s', newAp:'%s', apsInRange:'%s'\n" %(str(sta.params['associatedTo'][wlan]), str(aps_temp[v_cer.argmax()]), str(aps_temp)))
			#print('{"time":"%s", "sta":"%s", "oldAp":"%s", "newAp":"%s", "apsInRange":"%s", "battery":"%s", "position": "%s"}\n' %(str(time_selec*1000),str(sta.name),str(sta.params['associatedTo'][wlan]), str(aps_temp[v_cer.argmax()]), str(aps_temp), str(sta.params['battery']), str(sta.params['position'])))
			f.write('{"time":"%s", "sta":"%s", "oldAp":"%s", "newAp":"%s", "apsInRange":"%s", "battery":"%s", "position": "%s"}\n' %(str(time_selec*1000),str(sta.name),str(sta.params['associatedTo'][wlan]), str(aps_temp[v_cer.argmax()]), str(aps_temp), str(sta.params['battery']), str(sta.params['position'])))
			#f.write('{"time":"%s", "sta":"%s", "apsInRange":"%s", "battery":"%s", "position": "%s", "oldAp":"%s", "newAp":"%s"}\n' %(str(time_selec*1000),str(sta.name), str(aps_temp), str(sta.params['battery']), str(sta.params['position']), str(sta.params['associatedTo'][wlan]), str(aps_temp[v_cer.argmax()])))
			f.close()
			debug('iw dev %s disconnect\n' % sta.params['wlan'][wlan])
			sta.pexec('iw dev %s disconnect' % sta.params['wlan'][wlan])
			Association.associate_infra(sta, sta.params['apsInRange'][v_cer.argmax()], wlan=wlan, ap_wlan=ap_wlan)
			sta.params['battery'] = sta.params['battery'] - 0.1
			#sta.params['battery'] = sta.params['battery'] - (0.01 * sta.get_distance_to(sta.params['associatedTo'][wlan]))
			#print("assoc_py node: %s - battery: %s" % (sta.name, str(sta.params['battery'])))
			
		else:
			print('misma red')
		
		return self.changeAP

	def saw2(self, sta, ap, wlan, ap_wlan):
		#SAW: Simple Additive Weighting
		print("\n---SAW---")
		tiempo_inicial = time.time() 
		md = np.array([])						#MATRIZ DE DECISION
		#mp = np.array([ 2./6, 1./6, 3./6])		#VECTOR DE PESOS
		mp = np.array([ 2./5., 2./5., 1./5.])
		Alist = [r for r in md]
		aps_temp = []
		
		for i in range( len(sta.params["apsInRange"]) ):
			ap_temp = sta.params['apsInRange'][i]
			rssi_aptemp = sta.get_rssi(ap_temp,0,sta.get_distance_to(ap_temp))
			n_est_aptemp = len(ap_temp.params['associatedStations'])
			dis_to_aptemp = sta.get_distance_to(ap_temp)
			"""
			print ("AP name %s" %ap_temp.name )
			print ("RSSI %s" %str(rssi_aptemp) )
			print ("# estations %s" %str(n_est_aptemp) )
			print ("Distance to AP %s" %str(dis_to_aptemp) )
			"""
			#newrow = [ap_temp.name, rssi_aptemp, n_est_aptemp, dis_to_aptemp]
			#newrow = [rssi_aptemp, n_est_aptemp*-1, dis_to_aptemp*1000]
			newrow = [rssi_aptemp*-1, n_est_aptemp, dis_to_aptemp]
			Alist.append(newrow)
			aps_temp.append(ap_temp.name)
		
		md = np.array(Alist)
		"""
		print(aps_temp)
		print(md)
		print(mp)
		"""
		#maximos de cada columna de la matriz de decision
		m2 = md.min(axis=0)
		#print ("max")
		#print m2
		#matriz de decision sobre el vector de maximos
		m3 = m2/md
		#print ("m3")
		#print m3
		
		# multiplicar por el vector de pesos
		m4 = m3 * mp
		#print ("m4")
		#print m4
		
		#suma de las filas (vector de cercanias)
		v_cer = m4.sum(axis=1)
		#print ("m5")
		#print v_cer
		
		#mejor red
		#print ("mejor red puntaje")
		#print(v_cer.max())
		#Posicion del argumento maximo
		#print ("mejor red posicion")
		#print(v_cer.argmax())
		
		
		if str(sta.params['associatedTo'][wlan]) != aps_temp[v_cer.argmax()]:
			tiempo_final = time.time()
			time_selec = tiempo_final - tiempo_inicial
			f= open("/home/mininet/Escritorio/scripts/output/saw.txt","a+")
			print('diferente red')
			print("**************************method execution**************************")
			print ("aps")
			print(aps_temp)
			print ("matriz decision")
			print(md)
			print ("vector pesos")
			print(mp)
			print ("vector cercanias")
			print v_cer
			print ("mejor red puntaje")
			print(v_cer.max())
			#Posicion del argumento maximo
			print ("mejor red posicion")
			print(v_cer.argmax())
			"""
			print('\n---------------------------------------')
			print('Old AP: ' + str(sta.params['associatedTo'][wlan]))
			print('New AP: ' + str(sta.params['apsInRange'][v_cer.argmax()].name))
			print('New AP2: ' + str(aps_temp[v_cer.argmax()]))
			print('New AP: ' + str(sta.params['apsInRange']))
			"""
			#f.write('\n\n---------------------------------------')
			#f.write('\nOld AP: ' + str(sta.params['associatedTo'][wlan]))
			#f.write('\nNew AP: ' + str(aps_temp[v_cer.argmax()]))
			#f.write('\nAps in Range: ' + str(sta.params['apsInRange']))
			#f.write("{}, {}, {}\n".format(str(sta.params['associatedTo'][wlan]), str(aps_temp[v_cer.argmax()]), str(aps_temp)))
			#f.write("oldAp:'%s', newAp:'%s', apsInRange:'%s'\n" %(str(sta.params['associatedTo'][wlan]), str(aps_temp[v_cer.argmax()]), str(aps_temp)))
			#print('{"time":"%s", "sta":"%s", "oldAp":"%s", "newAp":"%s", "apsInRange":"%s", "battery":"%s", "position": "%s"}\n' %(str(time_selec*1000),str(sta.name),str(sta.params['associatedTo'][wlan]), str(aps_temp[v_cer.argmax()]), str(aps_temp), str(sta.params['battery']), str(sta.params['position'])))
			f.write('{"time":"%s", "sta":"%s", "oldAp":"%s", "newAp":"%s", "apsInRange":"%s", "battery":"%s", "position": "%s"}\n' %(str(time_selec*1000),str(sta.name),str(sta.params['associatedTo'][wlan]), str(aps_temp[v_cer.argmax()]), str(aps_temp), str(sta.params['battery']), str(sta.params['position'])))
			#f.write('{"time":"%s", "sta":"%s", "apsInRange":"%s", "battery":"%s", "position": "%s", "oldAp":"%s", "newAp":"%s"}\n' %(str(time_selec*1000),str(sta.name), str(aps_temp), str(sta.params['battery']), str(sta.params['position']), str(sta.params['associatedTo'][wlan]), str(aps_temp[v_cer.argmax()])))
			f.close()
			debug('iw dev %s disconnect\n' % sta.params['wlan'][wlan])
			sta.pexec('iw dev %s disconnect' % sta.params['wlan'][wlan])
			Association.associate_infra(sta, sta.params['apsInRange'][v_cer.argmax()], wlan=wlan, ap_wlan=ap_wlan)
			sta.params['battery'] = sta.params['battery'] - 0.1
			#print("assoc_py node: %s - battery: %s" % (sta.name, str(sta.params['battery'])))
			
		else:
			print('misma red')
		
		return self.changeAP

	def rf_V5_3_SIN_Group_movility(self, sta, ap, wlan, ap_wlan):
		#rf_V5_3_SIN_Group_movility
		#rf_V5_3: Random Forest final(SIN implementacion de movilidad en grupo) con este se elimina el efecto pong pong de RF_V2_0 -- 
		print("\n---RF---")
		tiempo_inicial = time.time() 
		"""
		aps = ""
		for n in range( len(sta.params["apsInRange"]) ):
			ap_temp2 = sta.params['apsInRange'][n]
			aps = aps + ap_temp2.name[2:]
		"""
		ap_names = ["ap1","ap2","ap3","ap4"]
		ind = False
		
		list_rf = []
		
		for i in range(len(ap_names)):
			for i2 in range( len(sta.params["apsInRange"]) ):
				ap_temp = sta.params['apsInRange'][i2]
				ap_temp_name = str(ap_temp.name)
				
				if ap_names[i] == ap_temp_name:
					
					# RSSI
					ap_temp_dis = sta.get_distance_to(ap_temp) # distancia del adispositivo al AP
					ap_temp_rssi = sta.get_rssi(ap_temp,0,ap_temp_dis)  #RSSI del dispositivo al AP
					"""
					if ap_temp_name == str(sta.params['associatedTo'][wlan]): # si el AP que esta escaneando es igual al Ap al que esta conectado:
						ap_temp_rssi = sta.get_rssi(ap_temp,0,ap_temp_dis)  # RSSI del dispositivo al AP se mantiene
					else: #si el AP que esta escaneando es DIFERENTE al Ap al que esta conectado:
						ap_temp_rssi = sta.get_rssi(ap_temp,0,ap_temp_dis) #RSSI del dispositivo al AP se le resta 2
					"""
					
					
					# BATERIA
					sta_app = sta.params.get("app", 1) #Se saca que aplicacion (ninguna-1, voz-2, audio-3, video-4) corre el dispositivo
					ap_temp_con = 0.001 * ap_temp_dis * sta_app #consumo de bateria (depende de la distancia y la aplicacion del dispositivo)
					#print("ap: " + str(ap_temp.name) + " distancia: " + str(ap_temp_dis) + " app: " + str(sta_app) + " bat_temp" + str(ap_temp_con))
					"""
					if ap_temp_name == str(sta.params['associatedTo'][wlan]): # si el AP que esta escaneando es igual al Ap al que esta conectado:
						ap_temp_con = 0.001 * ap_temp_dis * sta_app  # RSSI del dispositivo al AP se mantiene
					else: #si el AP que esta escaneando es DIFERENTE al Ap al que esta conectado:
						ap_temp_con = (0.001 * ap_temp_dis * sta_app)  #RSSI del dispositivo al AP se le resta 2
					"""
					
					# OCUPACION
					if ap_temp_name == str(sta.params['associatedTo'][wlan]): # si el AP que esta escaneando es igual al Ap al que esta conectado:
						ap_temp_num_sta = len(ap_temp.params['associatedStations']) # el numero de dispositivos se mantiene
					else: #si el AP que esta escaneando es DIFERENTE al Ap al que esta conectado:
						ap_temp_num_sta = len(ap_temp.params['associatedStations']) + 2 # al numero de dispositivos se le aumenta 2
					#ap_temp_num_sta = len(ap_temp.params['associatedStations'])
					
					ap_temp_ocu = ((ap_temp_num_sta*100.)/ap_temp.params['maxDis']) # se saca la ocupacion del AP en porcentaje
					
					# Escribir datos en dataset
					#f_datos_entrenamiento.write("{},{},{},{:.4f},".format(str(ap_temp.name), str(ap_temp_rssi), str(ap_temp_ocu),ap_temp_con))
					
					#f_datos_entrenamiento.write("{},{},{},{:.4f},".format("1", str(ap_temp_rssi), str(ap_temp_ocu), ap_temp_con))
					
					temp_list_rf = [1, ap_temp_rssi, ap_temp_ocu, ap_temp_con]
					
					list_rf.extend(temp_list_rf)
					
					ind = True
					break
				else:
					ind = False
				
			if ind == False:
				temp_list_rf = [0, -100.0, 100, 1.0]
				list_rf.extend(temp_list_rf)
				#f_datos_entrenamiento.write("{},{},{},{},".format("0", "xx", "yy","zz"))
		print("---------Array a predecir---------")
		print(list_rf)
		solution = pred([list_rf])
		ap_n = "ap{}".format(solution[0])
		
		aps_in_range_name = []
		rssi_aps_in_range = []
		for n in range( len(sta.params["apsInRange"]) ):
			ap_temp2 = sta.params['apsInRange'][n]
			aps_in_range_name.append(ap_temp2.name)
			
			rssi_aptemp = sta.get_rssi(ap_temp2,0,sta.get_distance_to(ap_temp2))
			rssi_aps_in_range.append(rssi_aptemp)
			
			#aps = aps + ap_temp2.name[2:]
		
		print("aps en rango")
		print(aps_in_range_name)
		
		print("RSSI aps en rango")
		print(rssi_aps_in_range)
		
		print("aps seleccionado")
		print(ap_n)
		
		hist = sta.params.get("hist", "null")
		
		if hist != "null":
			print("2_ SI tiene hist")
			if ap_n in aps_in_range_name:
				print("2_ AP predicho SI esta entre los aps en rango")
				hist_scan = hist[3] # se saca el historial de aps_predichos
				ap_ejm = hist_scan[0] # se saca del historial un ap para comparar con los demas
				print(ap_ejm)
				mode = 1
				for i in hist_scan[1:]: #ciclo para escanear todo el historial de aps_predichos
					if ap_ejm == i: #condicion para comparar los aps 
						mode = mode+1
					else: 
						break #si no son iguales se rompe el ciclo
				print(hist_scan)
				print("mode = " + str(mode))
				
				if mode == 6: # si el historial de aps predichos son todos iguales se pasa a la siguiente etapa
					print("La moda es igual")
					if str(sta.params['associatedTo'][wlan]) != str(ap_n):
						print("2_SI SE REALIZA EL CAMBIO")
						tiempo_final = time.time()
						time_selec = tiempo_final - tiempo_inicial
						f= open("/home/mininet/Escritorio/scripts/output/rf.txt","a+")
						f.write("2_inicio del cambio el ap al que esta conectado ya no esta en rango\n")
						indice = aps_in_range_name.index(str(ap_n))
						f.write('{"time":"%s","sta":"%s", "oldAp":"%s", "newAp":"%s", "apsInRange":"%s", "battery":"%s", "position": "%s"}\n' %(str(time_selec*1000),str(sta.name),str(sta.params['associatedTo'][wlan]), str(sta.params['apsInRange'][indice]), str(aps_in_range_name), str(sta.params['battery']), str(sta.params['position'])))
						f.write("2_fin del cambio\n")
						print ("2_CAMBIO.................................................................................")
						debug('iw dev %s disconnect\n' % sta.params['wlan'][wlan])
						sta.pexec('iw dev %s disconnect' % sta.params['wlan'][wlan])
						Association.associate_infra(sta, sta.params['apsInRange'][indice], wlan=wlan, ap_wlan=ap_wlan)
						sta.params['battery'] = sta.params['battery'] - 0.1
						#sta.params['battery'] = sta.params['battery'] - (0.01 * sta.get_distance_to(sta.params['associatedTo'][wlan]))
						f.close()
					else:
						print("2_NO SE REALIZA EL CAMBIO - misma red")
				else:
					print("La moda es menor")
				
				del hist[3][0]
				#print(hist)
				hist[3].append(ap_n)
			else:
				print("2_ AP predicho NO esta entre los aps en rango")
				del hist[3][0]
				hist[3].append("")
				
		else:
			print("2_ NO tiene hist")
			if ap_n in aps_in_range_name:
				if str(sta.params['associatedTo'][wlan]) != str(ap_n):
					if str(sta.params['associatedTo'][wlan]) not in aps_in_range_name:
						tiempo_final = time.time()
						time_selec = tiempo_final - tiempo_inicial
						f= open("/home/mininet/Escritorio/scripts/output/rf.txt","a+")
						f.write("inicio del cambio el ap al que esta conectado ya no esta en rango\n")
						indice = aps_in_range_name.index(str(ap_n))
						f.write('{"time":"%s","sta":"%s", "oldAp":"%s", "newAp":"%s", "apsInRange":"%s", "battery":"%s", "position": "%s"}\n' %(str(time_selec*1000),str(sta.name),str(sta.params['associatedTo'][wlan]), str(sta.params['apsInRange'][indice]), str(aps_in_range_name), str(sta.params['battery']), str(sta.params['position'])))
						f.write("fin del cambio\n")
						print ("CAMBIO.................................................................................")
						debug('iw dev %s disconnect\n' % sta.params['wlan'][wlan])
						sta.pexec('iw dev %s disconnect' % sta.params['wlan'][wlan])
						Association.associate_infra(sta, sta.params['apsInRange'][indice], wlan=wlan, ap_wlan=ap_wlan)
						sta.params['battery'] = sta.params['battery'] - 0.1
						#sta.params['battery'] = sta.params['battery'] - (0.01 * sta.get_distance_to(sta.params['associatedTo'][wlan]))
						f.close()
					else:
						print("El ap al que esta concestado aun est en rango --- no se hace el cambio")
				else:
					#f_2.write("-------------------------NO Cambio de AP{}-------------------------\n".format(mode[0][0]))
					print('misma red')
			#if ap_n in aps_temp:
			else:
				print('*******AP NOOOO ESTA EN RANGO*******')
				#f_2.write('*******AP NOOOO ESTA EN RANGO*******')
				#f_2.write("{},{}\n".format(str(sta.params['associatedTo'][wlan]),ap_n))
		
		return self.changeAP

	def rf_V5_2(self, sta, ap, wlan, ap_wlan):
		#RF: Random Forest
		
		print("\n---RF---")
		tiempo_inicial = time.time() 
		"""
		aps = ""
		for n in range( len(sta.params["apsInRange"]) ):
			ap_temp2 = sta.params['apsInRange'][n]
			aps = aps + ap_temp2.name[2:]
		"""
		ap_names = ["ap1","ap2","ap3","ap4"]
		ind = False
		
		list_rf = []
		
		for i in range(len(ap_names)):
			for i2 in range( len(sta.params["apsInRange"]) ):
				ap_temp = sta.params['apsInRange'][i2]
				ap_temp_name = str(ap_temp.name)
				
				if ap_names[i] == ap_temp_name:
					
					# RSSI
					ap_temp_dis = sta.get_distance_to(ap_temp) # distancia del adispositivo al AP
					ap_temp_rssi = sta.get_rssi(ap_temp,0,ap_temp_dis)  #RSSI del dispositivo al AP
					"""
					if ap_temp_name == str(sta.params['associatedTo'][wlan]): # si el AP que esta escaneando es igual al Ap al que esta conectado:
						ap_temp_rssi = sta.get_rssi(ap_temp,0,ap_temp_dis)  # RSSI del dispositivo al AP se mantiene
					else: #si el AP que esta escaneando es DIFERENTE al Ap al que esta conectado:
						ap_temp_rssi = sta.get_rssi(ap_temp,0,ap_temp_dis) #RSSI del dispositivo al AP se le resta 2
					"""
					
					
					# BATERIA
					sta_app = sta.params.get("app", 1) #Se saca que aplicacion (ninguna-1, voz-2, audio-3, video-4) corre el dispositivo
					ap_temp_con = 0.001 * ap_temp_dis * sta_app #consumo de bateria (depende de la distancia y la aplicacion del dispositivo)
					#print("ap: " + str(ap_temp.name) + " distancia: " + str(ap_temp_dis) + " app: " + str(sta_app) + " bat_temp" + str(ap_temp_con))
					"""
					if ap_temp_name == str(sta.params['associatedTo'][wlan]): # si el AP que esta escaneando es igual al Ap al que esta conectado:
						ap_temp_con = 0.001 * ap_temp_dis * sta_app  # RSSI del dispositivo al AP se mantiene
					else: #si el AP que esta escaneando es DIFERENTE al Ap al que esta conectado:
						ap_temp_con = (0.001 * ap_temp_dis * sta_app)  #RSSI del dispositivo al AP se le resta 2
					"""
					
					# OCUPACION
					if ap_temp_name == str(sta.params['associatedTo'][wlan]): # si el AP que esta escaneando es igual al Ap al que esta conectado:
						ap_temp_num_sta = len(ap_temp.params['associatedStations']) # el numero de dispositivos se mantiene
					else: #si el AP que esta escaneando es DIFERENTE al Ap al que esta conectado:
						ap_temp_num_sta = len(ap_temp.params['associatedStations']) + 2 # al numero de dispositivos se le aumenta 2
					#ap_temp_num_sta = len(ap_temp.params['associatedStations'])
					
					ap_temp_ocu = ((ap_temp_num_sta*100.)/ap_temp.params['maxDis']) # se saca la ocupacion del AP en porcentaje
					
					# Escribir datos en dataset
					#f_datos_entrenamiento.write("{},{},{},{:.4f},".format(str(ap_temp.name), str(ap_temp_rssi), str(ap_temp_ocu),ap_temp_con))
					
					#f_datos_entrenamiento.write("{},{},{},{:.4f},".format("1", str(ap_temp_rssi), str(ap_temp_ocu), ap_temp_con))
					
					temp_list_rf = [1, ap_temp_rssi, ap_temp_ocu, ap_temp_con]
					
					list_rf.extend(temp_list_rf)
					
					ind = True
					break
				else:
					ind = False
				
			if ind == False:
				temp_list_rf = [0, -100.0, 100, 1.0]
				list_rf.extend(temp_list_rf)
				#f_datos_entrenamiento.write("{},{},{},{},".format("0", "xx", "yy","zz"))
		print("---------Array a predecir---------")
		print(list_rf)
		solution = pred([list_rf])
		ap_n = "ap{}".format(solution[0])
		
		aps_in_range_name = []
		rssi_aps_in_range = []
		for n in range( len(sta.params["apsInRange"]) ):
			ap_temp2 = sta.params['apsInRange'][n]
			aps_in_range_name.append(ap_temp2.name)
			
			rssi_aptemp = sta.get_rssi(ap_temp2,0,sta.get_distance_to(ap_temp2))
			rssi_aps_in_range.append(rssi_aptemp)
			
			#aps = aps + ap_temp2.name[2:]
		
		print("aps en rango")
		print(aps_in_range_name)
		
		print("RSSI aps en rango")
		print(rssi_aps_in_range)
		
		print("aps seleccionado")
		print(ap_n)
		
		hist = sta.params.get("hist", "null")
		
		if hist != "null":
			print("2_con hist")
			#var = self.params.get("associatedTo", "null")[0]
			#print var
			#print(str(type(var)))
			if ap_n not in aps_in_range_name:
				#if type(var) == str:
				del hist[3][0]
				#print(hist)
				hist[3].append("")
				print("2_ap predicho no esta en rango")
				#print(hist)
				#print("es " + str(type(var)))
			else:
				hist_scan = hist[3]
				ap_ejm = hist_scan[0]
				print(ap_ejm)
				mode = 1
				for i in hist_scan[1:]:
					if ap_ejm == i:
						mode = mode+1
					else: 
						break
				print(hist_scan)
				print("mode = " + str(mode))
				
				
				if mode == 14:
					if str(sta.params['associatedTo'][wlan]) != str(ap_n):
						tiempo_final = time.time()
						time_selec = tiempo_final - tiempo_inicial
						f= open("/home/mininet/Escritorio/scripts/output/rf.txt","a+")
						f.write("2_inicio del cambio el ap al que esta conectado ya no esta en rango\n")
						indice = aps_in_range_name.index(str(ap_n))
						f.write('{"time":"%s","sta":"%s", "oldAp":"%s", "newAp":"%s", "apsInRange":"%s", "battery":"%s", "position": "%s"}\n' %(str(time_selec*1000),str(sta.name),str(sta.params['associatedTo'][wlan]), str(sta.params['apsInRange'][indice]), str(aps_in_range_name), str(sta.params['battery']), str(sta.params['position'])))
						f.write("2_fin del cambio\n")
						print ("2_CAMBIO.................................................................................")
						debug('iw dev %s disconnect\n' % sta.params['wlan'][wlan])
						sta.pexec('iw dev %s disconnect' % sta.params['wlan'][wlan])
						Association.associate_infra(sta, sta.params['apsInRange'][indice], wlan=wlan, ap_wlan=ap_wlan)
						sta.params['battery'] = sta.params['battery'] - 0.1
						#sta.params['battery'] = sta.params['battery'] - (0.01 * sta.get_distance_to(sta.params['associatedTo'][wlan]))
						f.close()
					else:
						print('2_misma red')
				elif str(sta.params['associatedTo'][wlan]) not in aps_in_range_name:
						tiempo_final = time.time()
						time_selec = tiempo_final - tiempo_inicial
						f= open("/home/mininet/Escritorio/scripts/output/rf.txt","a+")
						f.write("2_1_inicio del cambio el ap al que esta conectado ya no esta en rango\n")
						indice = aps_in_range_name.index(str(ap_n))
						f.write('{"time":"%s","sta":"%s", "oldAp":"%s", "newAp":"%s", "apsInRange":"%s", "battery":"%s", "position": "%s"}\n' %(str(time_selec*1000),str(sta.name),str(sta.params['associatedTo'][wlan]), str(sta.params['apsInRange'][indice]), str(aps_in_range_name), str(sta.params['battery']), str(sta.params['position'])))
						f.write("2_1_fin del cambio\n")
						print ("2_1_CAMBIO_ el ap al que estaba conectado noesta en rango.................................................................................")
						debug('iw dev %s disconnect\n' % sta.params['wlan'][wlan])
						sta.pexec('iw dev %s disconnect' % sta.params['wlan'][wlan])
						Association.associate_infra(sta, sta.params['apsInRange'][indice], wlan=wlan, ap_wlan=ap_wlan)
						sta.params['battery'] = sta.params['battery'] - 0.1
						#sta.params['battery'] = sta.params['battery'] - (0.01 * sta.get_distance_to(sta.params['associatedTo'][wlan]))
						f.close()
				else:
					print("2_NO se hace el cambio, la moda es distinta de 3")
					print("El ap aun esta en rango")
					
				del hist[3][0]
				#print(hist)
				hist[3].append(ap_n)
				#print(hist)
				#print("NO, es " + str(type(var)))
		else:
			print("sin hist")
			if ap_n in aps_in_range_name:
				if str(sta.params['associatedTo'][wlan]) != str(ap_n):
					if str(sta.params['associatedTo'][wlan]) not in aps_in_range_name:
						tiempo_final = time.time()
						time_selec = tiempo_final - tiempo_inicial
						f= open("/home/mininet/Escritorio/scripts/output/rf.txt","a+")
						f.write("inicio del cambio el ap al que esta conectado ya no esta en rango\n")
						indice = aps_in_range_name.index(str(ap_n))
						f.write('{"time":"%s","sta":"%s", "oldAp":"%s", "newAp":"%s", "apsInRange":"%s", "battery":"%s", "position": "%s"}\n' %(str(time_selec*1000),str(sta.name),str(sta.params['associatedTo'][wlan]), str(sta.params['apsInRange'][indice]), str(aps_in_range_name), str(sta.params['battery']), str(sta.params['position'])))
						f.write("fin del cambio\n")
						print ("CAMBIO.................................................................................")
						debug('iw dev %s disconnect\n' % sta.params['wlan'][wlan])
						sta.pexec('iw dev %s disconnect' % sta.params['wlan'][wlan])
						Association.associate_infra(sta, sta.params['apsInRange'][indice], wlan=wlan, ap_wlan=ap_wlan)
						sta.params['battery'] = sta.params['battery'] - 0.1
						#sta.params['battery'] = sta.params['battery'] - (0.01 * sta.get_distance_to(sta.params['associatedTo'][wlan]))
						f.close()
					else:
						print("El ap al que esta concestado aun est en rango --- no se hace el cambio")
				else:
					#f_2.write("-------------------------NO Cambio de AP{}-------------------------\n".format(mode[0][0]))
					print('misma red')
			#if ap_n in aps_temp:
			else:
				print('*******AP NOOOO ESTA EN RANGO*******')
				#f_2.write('*******AP NOOOO ESTA EN RANGO*******')
				#f_2.write("{},{}\n".format(str(sta.params['associatedTo'][wlan]),ap_n))
			
		return self.changeAP



	def rf_V5_1(self, sta, ap, wlan, ap_wlan):
		#RF: Random Forest
		print("\n---RF---")
		tiempo_inicial = time.time() 
		"""
		aps = ""
		for n in range( len(sta.params["apsInRange"]) ):
			ap_temp2 = sta.params['apsInRange'][n]
			aps = aps + ap_temp2.name[2:]
		"""
		ap_names = ["ap1","ap2","ap3","ap4"]
		ind = False
		
		list_rf = []
		
		for i in range(len(ap_names)):
			for i2 in range( len(sta.params["apsInRange"]) ):
				ap_temp = sta.params['apsInRange'][i2]
				ap_temp_name = str(ap_temp.name)
				
				if ap_names[i] == ap_temp_name:
					
					# RSSI
					ap_temp_dis = sta.get_distance_to(ap_temp) # distancia del adispositivo al AP
					ap_temp_rssi = sta.get_rssi(ap_temp,0,ap_temp_dis)  #RSSI del dispositivo al AP
					"""
					if ap_temp_name == str(sta.params['associatedTo'][wlan]): # si el AP que esta escaneando es igual al Ap al que esta conectado:
						ap_temp_rssi = sta.get_rssi(ap_temp,0,ap_temp_dis)  # RSSI del dispositivo al AP se mantiene
					else: #si el AP que esta escaneando es DIFERENTE al Ap al que esta conectado:
						ap_temp_rssi = sta.get_rssi(ap_temp,0,ap_temp_dis) #RSSI del dispositivo al AP se le resta 2
					"""
					
					
					# BATERIA
					sta_app = sta.params.get("app", 1) #Se saca que aplicacion (ninguna-1, voz-2, audio-3, video-4) corre el dispositivo
					ap_temp_con = 0.001 * ap_temp_dis * sta_app #consumo de bateria (depende de la distancia y la aplicacion del dispositivo)
					#print("ap: " + str(ap_temp.name) + " distancia: " + str(ap_temp_dis) + " app: " + str(sta_app) + " bat_temp" + str(ap_temp_con))
					"""
					if ap_temp_name == str(sta.params['associatedTo'][wlan]): # si el AP que esta escaneando es igual al Ap al que esta conectado:
						ap_temp_con = 0.001 * ap_temp_dis * sta_app  # RSSI del dispositivo al AP se mantiene
					else: #si el AP que esta escaneando es DIFERENTE al Ap al que esta conectado:
						ap_temp_con = (0.001 * ap_temp_dis * sta_app)  #RSSI del dispositivo al AP se le resta 2
					"""
					
					# OCUPACION
					if ap_temp_name == str(sta.params['associatedTo'][wlan]): # si el AP que esta escaneando es igual al Ap al que esta conectado:
						ap_temp_num_sta = len(ap_temp.params['associatedStations']) # el numero de dispositivos se mantiene
					else: #si el AP que esta escaneando es DIFERENTE al Ap al que esta conectado:
						ap_temp_num_sta = len(ap_temp.params['associatedStations']) + 2 # al numero de dispositivos se le aumenta 2
					#ap_temp_num_sta = len(ap_temp.params['associatedStations'])
					
					ap_temp_ocu = ((ap_temp_num_sta*100.)/ap_temp.params['maxDis']) # se saca la ocupacion del AP en porcentaje
					
					# Escribir datos en dataset
					#f_datos_entrenamiento.write("{},{},{},{:.4f},".format(str(ap_temp.name), str(ap_temp_rssi), str(ap_temp_ocu),ap_temp_con))
					
					#f_datos_entrenamiento.write("{},{},{},{:.4f},".format("1", str(ap_temp_rssi), str(ap_temp_ocu), ap_temp_con))
					
					temp_list_rf = [1, ap_temp_rssi, ap_temp_ocu, ap_temp_con]
					
					list_rf.extend(temp_list_rf)
					
					ind = True
					break
				else:
					ind = False
				
			if ind == False:
				temp_list_rf = [0, -100.0, 100, 1.0]
				list_rf.extend(temp_list_rf)
				#f_datos_entrenamiento.write("{},{},{},{},".format("0", "xx", "yy","zz"))
		print("---------Array a predecir---------")
		print(list_rf)
		solution = pred([list_rf])
		ap_n = "ap{}".format(solution[0])
		
		aps_in_range_name = []
		rssi_aps_in_range = []
		for n in range( len(sta.params["apsInRange"]) ):
			ap_temp2 = sta.params['apsInRange'][n]
			aps_in_range_name.append(ap_temp2.name)
			
			rssi_aptemp = sta.get_rssi(ap_temp2,0,sta.get_distance_to(ap_temp2))
			rssi_aps_in_range.append(rssi_aptemp)
			
			#aps = aps + ap_temp2.name[2:]
		
		print("aps en rango")
		print(aps_in_range_name)
		
		print("RSSI aps en rango")
		print(rssi_aps_in_range)
		
		print("aps seleccionado")
		print(ap_n)
		
		hist = sta.params.get("hist", "null")
		
		if hist != "null":
			print("2_con hist")
			#var = self.params.get("associatedTo", "null")[0]
			#print var
			#print(str(type(var)))
			if ap_n not in aps_in_range_name:
				#if type(var) == str:
				del hist[3][0]
				#print(hist)
				hist[3].append("")
				print("2_ap predicho no esta en rango")
				#print(hist)
				#print("es " + str(type(var)))
			else:
				hist_scan = hist[3]
				ap_ejm = hist_scan[0]
				print(ap_ejm)
				mode = 1
				for i in hist_scan[1:]:
					if ap_ejm == i:
						mode = mode+1
					else: 
						break
				print(hist_scan)
				print("mode = " + str(mode))
				
				
				if mode == 11:
					if str(sta.params['associatedTo'][wlan]) != str(ap_n):
						tiempo_final = time.time()
						time_selec = tiempo_final - tiempo_inicial
						f= open("/home/mininet/Escritorio/scripts/output/rf.txt","a+")
						f.write("2_inicio del cambio el ap al que esta conectado ya no esta en rango\n")
						indice = aps_in_range_name.index(str(ap_n))
						f.write('{"time":"%s","sta":"%s", "oldAp":"%s", "newAp":"%s", "apsInRange":"%s", "battery":"%s", "position": "%s"}\n' %(str(time_selec*1000),str(sta.name),str(sta.params['associatedTo'][wlan]), str(sta.params['apsInRange'][indice]), str(aps_in_range_name), str(sta.params['battery']), str(sta.params['position'])))
						f.write("2_fin del cambio\n")
						print ("2_CAMBIO.................................................................................")
						debug('iw dev %s disconnect\n' % sta.params['wlan'][wlan])
						sta.pexec('iw dev %s disconnect' % sta.params['wlan'][wlan])
						Association.associate_infra(sta, sta.params['apsInRange'][indice], wlan=wlan, ap_wlan=ap_wlan)
						sta.params['battery'] = sta.params['battery'] - 0.1
						#sta.params['battery'] = sta.params['battery'] - (0.01 * sta.get_distance_to(sta.params['associatedTo'][wlan]))
						f.close()
					else:
						print('2_misma red')
				elif str(sta.params['associatedTo'][wlan]) not in aps_in_range_name:
						tiempo_final = time.time()
						time_selec = tiempo_final - tiempo_inicial
						f= open("/home/mininet/Escritorio/scripts/output/rf.txt","a+")
						f.write("2_1_inicio del cambio el ap al que esta conectado ya no esta en rango\n")
						indice = aps_in_range_name.index(str(ap_n))
						f.write('{"time":"%s","sta":"%s", "oldAp":"%s", "newAp":"%s", "apsInRange":"%s", "battery":"%s", "position": "%s"}\n' %(str(time_selec*1000),str(sta.name),str(sta.params['associatedTo'][wlan]), str(sta.params['apsInRange'][indice]), str(aps_in_range_name), str(sta.params['battery']), str(sta.params['position'])))
						f.write("2_1_fin del cambio\n")
						print ("2_1_CAMBIO_ el ap al que estaba conectado noesta en rango.................................................................................")
						debug('iw dev %s disconnect\n' % sta.params['wlan'][wlan])
						sta.pexec('iw dev %s disconnect' % sta.params['wlan'][wlan])
						Association.associate_infra(sta, sta.params['apsInRange'][indice], wlan=wlan, ap_wlan=ap_wlan)
						sta.params['battery'] = sta.params['battery'] - 0.1
						#sta.params['battery'] = sta.params['battery'] - (0.01 * sta.get_distance_to(sta.params['associatedTo'][wlan]))
						f.close()
				else:
					print("2_NO se hace el cambio, la moda es distinta de 3")
					print("El ap aun esta en rango")
					
				del hist[3][0]
				#print(hist)
				hist[3].append(ap_n)
				#print(hist)
				#print("NO, es " + str(type(var)))
		else:
			print("sin hist")
			if ap_n in aps_in_range_name:
				if str(sta.params['associatedTo'][wlan]) != str(ap_n):
					if str(sta.params['associatedTo'][wlan]) not in aps_in_range_name:
						tiempo_final = time.time()
						time_selec = tiempo_final - tiempo_inicial
						f= open("/home/mininet/Escritorio/scripts/output/rf.txt","a+")
						f.write("inicio del cambio el ap al que esta conectado ya no esta en rango\n")
						indice = aps_in_range_name.index(str(ap_n))
						f.write('{"time":"%s","sta":"%s", "oldAp":"%s", "newAp":"%s", "apsInRange":"%s", "battery":"%s", "position": "%s"}\n' %(str(time_selec*1000),str(sta.name),str(sta.params['associatedTo'][wlan]), str(sta.params['apsInRange'][indice]), str(aps_in_range_name), str(sta.params['battery']), str(sta.params['position'])))
						f.write("fin del cambio\n")
						print ("CAMBIO.................................................................................")
						debug('iw dev %s disconnect\n' % sta.params['wlan'][wlan])
						sta.pexec('iw dev %s disconnect' % sta.params['wlan'][wlan])
						Association.associate_infra(sta, sta.params['apsInRange'][indice], wlan=wlan, ap_wlan=ap_wlan)
						sta.params['battery'] = sta.params['battery'] - 0.1
						#sta.params['battery'] = sta.params['battery'] - (0.01 * sta.get_distance_to(sta.params['associatedTo'][wlan]))
						f.close()
					else:
						print("El ap al que esta concestado aun est en rango --- no se hace el cambio")
				else:
					#f_2.write("-------------------------NO Cambio de AP{}-------------------------\n".format(mode[0][0]))
					print('misma red')
			#if ap_n in aps_temp:
			else:
				print('*******AP NOOOO ESTA EN RANGO*******')
				#f_2.write('*******AP NOOOO ESTA EN RANGO*******')
				#f_2.write("{},{}\n".format(str(sta.params['associatedTo'][wlan]),ap_n))
			
		return self.changeAP



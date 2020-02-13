#!usr/bin/python

import sys
import re

#funzione che prende in input una cigar di una read e il valore mapq
#restituisce una lista binaria

def parseCigar(cigar, mapq):	
	cigar_expr = '(\d+)([A-Z]+)'
	cigar_list = re.findall(cigar_expr, cigar)
	print(cigar_list)
	#lista binaria 
	s = []		 
	for i in cigar_list:
		#match/mismatch
		if i[1] == 'M':
			if mapq != '*':
				#mapq >= 30 base buona, sono match
				if int(mapq) >= 30: 
					s = s + [1] * int(i[0])
				#controllo della qualità che porta ai mismatch
				#mapq < 30
				else:
					s = s + [0] * int(i[0])
			#se mapq non è definito considero M come match
			else:
				s = s + [1] * int(i[0])
		#inserimento, bisogna mettere lo 0?
		if i[1] == 'I':
			s = s + [0] * int(i[0])
		#delezione, non bisogna mettere lo 0?
		if i[1] == 'D':
			s = s
		#allineamenti spliced
		if i[1] == 'N':
			s = s + [0] * int(i[0])
		#soft clipping
		if i[1] == 'S':
			s = s + [0] * int(i[0])
		#hard clipping
		#caso di h è da non considerare?
		if i[1] == 'H':
			s = s	
		#delezione silente(padding)	
		if i[1] == 'P':
			s = s + [0] * int(i[0])
	return s

#funzione confronto
#prende in input la copertura vecchia, la cigar binaria, e la posizione di inizio della read
#restituisce la copertura aggiornata

def confronto(copertura, cigar, pos_i):
	pos = int(pos_i)
	for i in cigar:
		copertura[pos] = copertura[pos] + i
		pos = pos + 1
	return copertura
	
#stampa della copertura su file
#prende in input la copertura

def stampa(copertura):
	f = open('output.txt', 'w')
	f.write(str(copertura))


def stampa(copertura, ref):
	f.write("Copertura per la reference " + ref + ": \n") 
	for i in copertura:
		f.write(str(i) + " ")
	f.write("\n\n\n")	
	
#apertura del file

with open(sys.argv[1], 'r') as input_sam_file:
	sam_file = input_sam_file.read()

#espressioni regolari header_section

hd_expr = '^@HD\s+VN:(\d+\.\d+)(\s+SO:(\w+))?'
hd_obj = re.search(hd_expr, sam_file, re.M)
hd_vn = hd_obj.group(1)
hd_so = hd_obj.group(3)
print("Header Section, record @HD:")
print(hd_vn, hd_so, "\n")

sq_expr = '^@SQ\s+SN:(\w+)\s+LN:(\w+)'
sq_list = re.findall(sq_expr, sam_file, re.M)
print("Header Section, record @SQ:")
print(sq_list, "\n")


'''
rg_expr = '^@RG\s+ID:(\w+)\s+SM:(\w+)'
rg_list = re.findall(rg_expr, sam_file, re.M)
print(rg_list)

pg_expr = '@PG\s+ID:(\w+)'	
pg_list = re.findall(pg_expr, sam_file, re.M)
print(pg_list)

'''

#espressioni regolari alignment_section

#condizione da tenere in considerazione: 
#il nome della read deve iniziare con un carattere non speciale  
#i caratteri speciali che è possibile usare sono '/', '<', '>', '$', '?', '!', '-'
#considero che i campi 1, 3, 5 e 6 possano avere come valore anche *(campo inesistente)

#posizione dei campi 
#                  1	        2	     3		   4	     5	      6	

asec_expr = '^(\w+[\w*/*<*>*\$*\?*!*\-*]*)\s+(\d+)\s+(\w+|\*)\s+(\d+)\s+(\d+|\*)\s(\w+|\*)'
asec_obj = re.findall(asec_expr, sam_file, re.M)
print("Alignment Section:")
print(asec_obj, "\n")

#inizializzazione delle coperture
#lavoro su una copertura alla volta per non avere problemi di memoria
k=0
for i in sq_list:
	copertura = [0] * int(i[1])
	#eseguo il confronto con le read
	for j in asec_obj:
		if j[2] == i[0]:
			#ho iniziato a fare il parsing della cigar						
			pc = parseCigar(j[5], j[4])
			print(pc)
			#confronto e aggiornamento della copertura
			copertura = confronto(copertura, pc, j[3])
			#stampa della copetura
	k= k + 1
	f = open('output' + str(k)+ '.txt', 'w')
	stampa(copertura, i[0])


#!/usr/bin/python
# encoding:latin1

import sys
import re
import binascii
import string
import random
import parser
import csv

from subprocess import call
from math import log

class Prova:
	def __init__(self,filename,disc = 'None', prof = 'None', title = 'None', subj='None', class_id = 'None'):
		self.file=open(filename,"w")
		self.file.close();
		self.filename=filename
		self.subj=subj

		self.START_TAG_PARTS = '\\begin{parts}\n'
		self.END_TAG_PARTS = '\\end{parts}\n'

		self.START_TAG_SOLUTION = '\\begin{{solution}}{0}\n'
		self.END_TAG_SOLUTION = '\\end{solution}\n'

		self.START_TAG_SOLUTIONLINES = '\\begin{{solutionorlines}}{0}\n'
		self.END_TAG_SOLUTIONLINES = '\\end{solutionorlines}\n'

		self._tag_solution_start=self.START_TAG_SOLUTION
		self._tag_solution_end=self.END_TAG_SOLUTION

		self._solution_types = [ 'space' , 'lines' ]
		self._solution_type = 'space'
		

		self.START_TAG_EQUATION = '\\begin{{eqnarray{0}}}\n'
		self.END_TAG_EQUATION = '\\end{{eqnarray{0}}}\n'

		# class number, ie 101, U, A, etc
		self.class_id=class_id

		# doctype exam, exercises, etc
		self.doctype = 'prova'

		# for writing solutions
		self.START_SOLUTION_PAGE = '\\clearpage\n'
		self.END_SOLUTION_PAGE = ''

		self.current_question 	= 0
		self.current_part 		= 0
		self.current_subpart 	= 0

		# solution modes
		self.solution_modes = [ 'last_page', 'per_question', 'None' ]
		self.solution_mode = 'None'
		
		self.solutions = [ '\\begin{center}\n','\\large{{textbf{{RESPOSTAS}}}}\n', '\\end{center}\n' ]

		# solution area
		self.solution_area = [ 'lines', 'blank' ]

		# title of the list/exam/etc
		if type(title) == type (''):
			self.title = title
		else:
			raise TypeError('title must be a string')

		if type(prof) == type (''):
			self.prof = prof
		else:
			raise TypeError('prof must be a string')

		if type(disc) == type (''):
			self.disc = disc
		else:
			raise TypeError('subj must be a string')

		random.seed()

	def save_file(self):
		call(["latex","-src","-output-format=pdf","-interaction=nonstopmode",self.filename," > /dev/null"])
		#call(["dvips","-o","output.ps","%.dvi"])

	def set_doctype(self,doctype):
		if doctype == 'lista':
			self.doctype = doctype
		elif doctype == 'prova':
			self.doctype = doctype
		else:
			raise TypeError("doctype parameter must be strings 'prova', 'lista'")

	def set_class_id(self,class_id):
		self.class_id = class_id

	def get_solution_type(self):
		return self._solution_type

	#def set_solution_type(self,solution_type)

	def write_preamble(self):

		with open(self.filename,'a') as doc:
			doc.write('\\documentclass{exam}\n')

			doc.write('\\usepackage[{0}]{{ifrstex}}\n'.format(self.doctype))

			doc.write('\\disciplina{{{0}}}\n'.format(self.disc))
			doc.write('\\professor{{{0}}}\n'.format(self.prof))

			if self.doctype == 'lista':
				doc.write('\\temadalista{{{0}}}\n'.format(self.title))
			elif self.doctype == 'prova':
				doc.write('\\nomedaprova{{{0}}}\n'.format(self.title))
				doc.write('\\assuntodaprova{{{0}}}\n'.format(self.subj))

			doc.write('\\turma{{{0}}}\n'.format(self.class_id))

			doc.write('\\begin{document}\n')

			doc.write('\\maketitle\n')

			doc.write('\\begin{questions}\n')
			
			doc.close()

	def write_end(self):

		##print self.solutions			

		with open(self.filename,'a') as doc:
			doc.write('\\end{questions}\n')

			if self.solution_mode == 'last_page':
				doc.write('\\clearpage \n')

				for lin in self.solutions:
					#print lin
					doc.write(lin+'\n')

			doc.write('\\end{document}\n')		
			
			doc.close()

	def set_solution_mode(self, solution_mode):
		if type(solution_mode) == type(''):	
			if solution_mode in set(self.solution_modes):
				print 'Solution mode: ' + solution_mode
				self.solution_mode = solution_mode
			else:
				raise NameError('solution_mode must be in', self.solution_modes)
		else:
			raise TypeError('solution_mode must be a string')
			
			
	def next_question(self):
		
		self.current_question += 1
		self.current_part = 1
		self.current_subpart = 1

		self.solutions.append('\\textbf{{QUESTÃO {0}}} \n'.format(self.current_question))

	def next_part(self):
		self.current_part += 1
		self.current_subpart = 1

	def next_subpart(self):
		self.current_subpart += 1

	def get_ref(self):
		return str(self.current_question)+"_"+str(self.current_part)+"_"+str(self.current_subpart)

	def get_solution_type(self):
		return self._solution_type

	def start_solution(self,space=''):
		if space=='':
			spac=''
		else:
			spac='['+space+']in'		

		if self.get_solution_type()=='space':
			string='\\begin{{solution}}{0}\n'.format(spac)
		elif self.get_solution_type()=='lines':
			string='\\begin{{solutionorlines}}{0}\n'.format(spac)
		else:
			raise(ValueError,"invalid solution type:")

		return string

	def end_solution(self):
		end_tag_solution=''
		if self.get_solution_type()=='solution':
			self._tag_solution_end=self.END_TAG_SOLUTION
		elif self.get_solution_type()=='solutionorlines':
			self._tag_solution_end=self.END_TAG_SOLUTIONORLINES

		return self._tag_solution_end

	def add_answer(self,answer,space=''):
		#print 'Adding answer...'
		#if self.solution_mode == 'per_question':

		if self.solution_mode == 'last_page':
			self.solutions.append('\\textbf{{ Item \\ref{{q:{0}}} }}: {1} \n'.format(self.get_ref(),answer))
			#self.add_answer('$'+str(nb2)+'_{{{0}}}$'.format(b2))


	#################################################
	# \brief Converts a number 'num' to base 'base' # 
	#################################################

	# \param num Number to be converted
	# \param base Target base. If method is polynomial, base should be the original base
	# \param method Convertion method to use: division ('div'), polynomial ('poly'), subtractions ('sub'), or substitution ('subst')
	# \return String representing the converted number and vector of intermediary steps taken

	# 25/03/2015: Corrected number convertion bug, added hex dictionary
	# 08/04/2015: Added support for step-by-step answer generation
	def conv2base(self,num,base,method,debug=False):
		numero = num
		

		hexdict = { i: str(i) for i in range(10) } 
		hexdict[10]='A'
		hexdict[11]='B'
		hexdict[12]='C'
		hexdict[13]='D'
		hexdict[14]='E'
		hexdict[15]='F'

		conv = []
		steps = []

		if method=='div':
			while (numero >= base):	
				div = numero/ base
				resto = numero % base

				steps.append(str(numero)+" & = \\bf{"+str(div)+"} \\cdot " +str(base)+" + "+str(resto) )

				conv.append (resto)
				numero = div
			
				#print 'mod: ', resto, '/ div:',  div
			
			steps.append( str(numero) + "& \\" )
			conv.append ( numero )

			text_conv = ''
			for digit in reversed (conv):
				text_conv+=hexdict[digit]

			return text_conv,steps
		
		elif method == 'sub':
			exp = 1

			while (pow(2,exp)<numero):
				exp+=1

			if exp<7:
				exp=7

			conv=''
			steps=[]
			while exp>=0:
				pot=pow(2,exp)
				ant=numero
				if pot<=numero:		
					res=str(numero-pot)
					numero-=pot
					digit='1'
				else:
					res='\\color{red}{X}'
					digit='0'

				conv+=digit
				steps.append(str(ant) + " - " + str(pot) + " &= " + res +" \\rightarrow & " + str(digit))

				exp-=1

			return conv,steps

		elif method == 'poly':
			digits = {}
			
			exp = 0
			while numero>0:
				digits[exp]=numero%10
				numero/=10
				exp+=1
	
			conv = sum( [digits[p]*pow(base,p) for p in digits.keys()] )

			# part 1: expoent expansion
			expanded = ""
			for p in digits.keys():
				tmp = str(digits[p])+" \\cdot "+str(base) + "^{" + str(p) + "}"
				if len(expanded) == 0:
					expanded=tmp
				else:
					expanded=tmp+"+"+expanded
				
			steps.append(expanded)
			#part 2: expoent calculation
			expoent_calc=""
			for p in digits.keys():
				tmp = str(digits[p])+" \\cdot "+str(pow(base,p))
				if len(expoent_calc) == 0:
					expoent_calc=tmp
				else:
					expoent_calc=tmp+"+"+expoent_calc

			steps.append(expoent_calc)

			#part 3: expoent multiplied by digits
			exp_mul_base=""
			for p in digits.keys():
				tmp = str(digits[p]*pow(base,p))
				if len(expoent_calc) == 0:
					exp_mul_base=tmp
				else:
					exp_mul_base=tmp+"+"+exp_mul_base

			steps.append(exp_mul_base)		
			steps.append(str(conv))

			return conv,steps														

		else:
			raise(ValueError,"method parameter must be in")

		

	def gen_nums(self,qtd,base=2,exp=6,maxval=255):
		questions=[]		

		maximum = min(pow(base,exp)-1,maxval)

		for num in range(qtd):

			while (True):	
				num1=random.randint(0,maximum) 
				num2=random.randint(0,maximum)
				if ([num1,num2] and [num2,num1] not in questions) and num1<=maxval and num2<=maxval:
					break
	
			questions.append([num1,num2])

		return questions

	def bin2dec(self,bitstream,nbits,rep):
		if rep == 'C2':
			if (bitstream[0]=='1'):
				return int(bitstream,2)-(1<<nbits)
			else:
				return int(bitstream,2)
		elif rep == 'pos' or rep == 'none' :
			return int(bitstream,2)

	def compl(self,bitstream,nbits):
		return int(bitstream,2)-int(1<<nbits)		

	def get_positive_sums(self,nbits=6,qtd=20,debug=False):

		answers = []
		questions = []

		for q in self.gen_nums(qtd):
			numbin1='{0:0>{fill}b}'.format(q[0],fill=nbits)
			numbin2='{0:0>{fill}b}'.format(q[1],fill=nbits)
			numbin3='{0:0>{fill}b}'.format(q[0]-q[1],fill=nbits)

			numbin3=numbin3[len(numbin3)-nbits:len(numbin3)]

			bin2dec1=str(bin2dec_pos(numbin1,nbits))
			bin2dec2=str(bin2dec_pos(numbin2,nbits))
			bin2dec3=str(bin2dec_pos(numbin3,nbits))

			answers.append(numbin1 + " (" + bin2dec1 + ")\t - " + numbin2 + " (" +bin2dec2 + ")\t= " + numbin3 + " (" + bin2dec3 + ")")
			questions.append(numbin1 + " - " + numbin2)

		return questions, answers

	def get_subs_pos(self,qtd=20,nbits=6,debug=False):
		answers = []
		questions = []

		for q in self.gen_nums(qtd):
			if q[0]>q[1]:
				n1=q[0] 
				n2=q[1]
			else:
				n1=q[1] 
				n2=q[0]
			

			numbin1='{0:0>{fill}b}'.format(n1,fill=nbits)
			numbin2='{0:0>{fill}b}'.format(n2,fill=nbits)

			numbin3='{0:0>{fill}b}'.format(n1-n2,fill=nbits)

			question= [numbin1,str(n1),numbin2,str(n2),numbin3,str(n1-n2)]
		
			questions.append(question)

		return questions

	##################################
	# \brief Adds a written question #
	##################################
	def add_question(self,enun,answer='',space='1in'):

		with open(self.filename,"a") as doc:
			enunciado='\\question {enun}. \\\\ \n'
			doc.write(enunciado.format(enun=enunciado))

			if answer!='':
				doc.add_answer(answer)
			doc.close()		

	def get_binary_sums(self,qtd,nbits,rep,operands,debug=False):

		#debug=False
		#nbits=6
		answers = []
		questions = []

		for q in operands:
			numbin1='{0:0>{fill}b}'.format(q[0],fill=nbits)
			numbin2='{0:0>{fill}b}'.format(q[1],fill=nbits)
			numbin3='{0:0>{fill}b}'.format(q[0]+q[1],fill=nbits)

			sinal_nbin1=numbin1[len(numbin1)-nbits]
			sinal_nbin2=numbin2[len(numbin2)-nbits]
			sinal_nbin3=numbin3[len(numbin3)-nbits]

			if rep == 'C2':
				if ((sinal_nbin1 == sinal_nbin2) and (sinal_nbin1 != sinal_nbin3)):
					OV="(ESTOURO)"
				else:
					OV=""
			elif rep == 'pos':
				if log(q[0]+q[1],2)>nbits:
					OV="(ESTOURO)"
				else:
					OV=""
			elif rep == 'none':
				OV = ""

			numbin3=numbin3[len(numbin3)-nbits:len(numbin3)]

			bin2dec1=str(self.bin2dec(numbin1,nbits,rep))
			bin2dec2=str(self.bin2dec(numbin2,nbits,rep))
			bin2dec3=str(self.bin2dec(numbin3,nbits,rep))				

			question= [numbin1,bin2dec1,numbin2,bin2dec2,numbin3,bin2dec3,OV]
		
			questions.append(question)
			
		if debug:
			for q in questions:
				print q

			for a in answers:
				print a

		return questions, operands

	#######################################################
	# \brief Add a question of computational convertion 
	#######################################################
	def add_question_comp_conv(self,qtd,nbits,operands=[],Borrow=False):
		
		rand.random(1,1024)

		print "Questão: conversão de grandezas computacionais"

		multipliers={}
		multipliers['K']=1
		multipliers['M']=2
		multipliers['G']=3

		if qtd>1:
			self.next_question()

		elif qtd==1:
			self.next_question()
			enun = '\\question Quantos {bits} bits representados como \\textbf{{{rep}}}'
		else:
			raise(ValueError,"parameter qtd must be numeric and greater or equal than 1")
						
	
	##################################################################################
	# \brief Add a question of binary subtraction, considering only positive numbers #
	##################################################################################

	# \param qtd Quantity of questions to generate
	# \param nbits Number os bits of the subtractions
	# \param Borrow if true, take into consideration a Borrow bit
	def add_question_sub_pos(self,qtd,nbits,Borrow=False):
		with open(self.filename,"a") as doc:

			print "Questão: subtração binária usando a representação de positivos sem sinal:"

			enun = '\\question Faça as seguintes subtrações de números binários de {bits} bits representados como \\textbf{{{rep}}}. Alem disso:\\\\ \n'.format(bits=nbits,rep="inteiros positivos sem sinal")
			enun+="\t\\begin{itemize} \\\\ \n"
			enun+="\t\t\\item Indique entre os parênteses os valores decimais dos números binários, tanto dos operandos quanto do resultado da soma \\\\ \n"
			enun+="\t\t\\item Quando houver estouro de representação, \\underline{explicando o porquê} \\\\ \n"
			enun+="\t\\end{itemize} \\\\ \n"

			self.next_question()

			doc.write(enun)

			doc.write(self.START_TAG_PARTS)

			for q in self.get_subs_pos(qtd,nbits):
				doc.write('\part ' + q[0] + '(\\qquad\\quad) - ' + q[2] + '(\\qquad\\quad) =\\qquad\\qquad\\qquad(\\qquad\\quad)\n')
				#prova.write(self.START_TAG_SOLUTION)
				resposta='{nb1} ({n1:3}) - {nb2} ({n2:3}) = {sub} ({subb:3})'
				resposta=resposta.format(nb1=q[0],n1=q[1],nb2=q[2],n2=q[3],sub=q[4],subb=q[5])
				print resposta

				#self.add_answer(resposta)
				#prova.write('\t' + resposta + '\n')
				#prova.write(self.END_TAG_SOLUTION)

				if self.solution_mode == 'per_question':

					doc.write(self.start_solution())
					doc.write('\t{}\n'.format(resposta))
					doc.write(self.end_solution())

				elif self.solution_mode == 'last_page':
					self.add_answer(resposta)


				self.next_part()

			doc.write(self.END_TAG_PARTS)

			doc.close()


	###########################################################################
	# \brief Add a binary sum question, either as positives or 2's complement #
	###########################################################################

	# \param qtd number of questions
	# \param nbits number of bits for the sums
	# \param rep numeric representation, either "C2", "pos", or 'none'
	# \param operands vector of operands [a,b] for the sum - skips random operand generation if set
	# \param enun question text
	# \return vector of operands [a,b] so it can be be used again on other exercises
	def add_question_sum(self,qtd,nbits,rep,operands=[],enun='',att=''):

		with open(self.filename,"a") as doc:

			if rep == 'C2':
				numeric_rep='Complemento de 2'
			elif rep == 'pos':
				numeric_rep='Positivos sem sinal'

			print "Questão: somas em {numeric_rep}".format(numeric_rep=numeric_rep)
			
			if enun == '':
				enun = '\\question Faça as seguintes somas de números binários de {bits} bits considerando a representação como \\textbf{{{rep}}}. Além disso:\\\\ \n'
				enun+="\t\\begin{{itemize}} \n"
				enun+="\t\t\\item Escreva entre os parênteses os valores decimais dos números binários, tanto dos operandos quanto do resultado da soma \\\\ \n"
				enun+="\t\t\\item Indique se houver estouro de representação, \\underline{{indicando o porquê}} \\\\ \n"
				enun+="\t\\end{{itemize}} \n"

			self.next_question()
			doc.write(enun.format(rep=numeric_rep,bits=nbits))
			doc.write(self.START_TAG_PARTS)

			if len(operands)==0:
				operands=self.gen_nums(qtd,base=2,exp=nbits,maxval=255)

			questions = []
			#if op == 'sum':
			questions, operands = self.get_binary_sums(qtd,nbits,rep,operands)				
			#elif op == 'sub' and rep == 'C2':
			#	negated_operands = [] if len(operands)==0 else [ [op[0],int(op[1],2)-1<<nbits] for op in operands ]
			#	print neg_operands
			#	questions = self.get_binary_sums(qtd,nbits,rep,negated_operands)			

			for q in questions:
				doc.write('\\part ' + q[0] + '(\\qquad\\quad) + ' + q[2] + '(\\qquad\\quad) = \\qquad\\qquad\\qquad(\\qquad\\quad)')
				doc.write(' \\label{' + self.get_ref() + '} \n')
						
				resposta = '{nb1} ({n1:3}) + {nb2} ({n2:3}) = {s} ({sb:3}) {ov}'.format(nb1=q[0],n1=q[1],nb2=q[2],n2=q[3],s=q[4],sb=q[5],ov=q[6])
				#self.add_answer(resposta)

				if self.solution_mode == 'per_question':

					doc.write(self.start_solution())
					doc.write('\t{}\n'.format(resposta))
					doc.write(self.end_solution())

				elif self.solution_mode == 'last_page':
					self.add_answer(resposta)

				print resposta
	
				self.next_part()

			doc.write(self.END_TAG_PARTS)

			doc.close()

			return operands

	def add_question_conv2base(self,qtd,src_minbase=2,src_maxbase=9,dst_minbase=2,dst_maxbase=9,method='div',text='Faça as seguintes conversões de base'):

		questions = []

		for nums in self.gen_nums(qtd,2,8):
			b1=random.randint(src_minbase,src_maxbase)
			b2=random.randint(dst_minbase,dst_maxbase)

			questions.append([[nums[0],b1],[nums[1],b2]])
				
		with open(self.filename,"a") as prova:

			self.next_part()

			print "Questões de conversão de base:"

			prova.write('\n\\question {}: \\\\ \n'.format(text))
			prova.write(self.START_TAG_PARTS)
			
			for q in questions:
				num1=q[0][0]
				num2=q[0][1]
				b1=q[0][1]
				b2=q[1][1]

				print num1, "na base ", b1, " para base ", b2

				steps=[]

				if b1!=10 and b2==10:
					# convertion to base 10, use polynomial method
					nb1,ignore=self.conv2base(num1,b1,'div')

					nb2,steps=self.conv2base(int(nb1),b1,'poly')

				elif b1<10 and b2<10:
					# if both original and destiny base lower than 10:
					# - converts number to base 10
					# - converts to destiny base
					nb1,ignore=self.conv2base(num1,b1,'div')

					tobase10,steps1=self.conv2base(int(nb1),b1,'poly')
					nb2,steps2=self.conv2base(int(tobase10),b2,'div')
					
					steps=steps1 + steps2

					print steps

				else:
					nb1,ignore=self.conv2base(num1,b1,method)
					nb2,steps=self.conv2base(num1,b2,method)
				

				enum='\\part ${}_{{{}}}$ para base {} \label{{q:{}}}\n'
				
				prova.write(enum.format(nb1,b1,b2,self.get_ref()))

				if self.solution_mode == 'per_question':
					prova.write(self.START_TAG_SOLUTION.format('')+self.START_TAG_EQUATION.format("*"))
					
					for s in steps:
						prova.write(s+" \\\\ \n")

					prova.write('\t{} \n'.format(nb2))

					prova.write(self.END_TAG_EQUATION.format("*")+self.END_TAG_SOLUTION)
				elif self.solution_mode == 'last_page':
					self.add_answer('$'+str(nb2)+'_{{{0}}}$'.format(b2))
				elif self.solution_mode != 'None':
					raise(ValueError,"self.solution_mode must be in")
					

				self.next_part()

			self.next_question()

			prova.write(self.END_TAG_PARTS)

			prova.close();

	def add_question_boolalg_demorgan(self,qtd=10):

		with open(self.filename,"a") as prova:

			enunciado='\n\\question Simplifique as seguintes equações booleanas:\\\\ \n'
			enunciado+='\\textbf{{DICA}}: A primeira propriedade que deve ser aplicada é o \emph{{{0}}}\n'

			prova.write(enunciado.format('Teorema de De-Morgan'))
			prova.write(self.START_TAG_PARTS)

			padrao1 = '\\part ${0} \\cdot \\barra{{{1}}} \\cdot {2} + \\barra{{ {1}\\cdot {2} }}$\n'
			padrao2 = '\\part $\\barra{{ {0} }} + \\barra{{ {0} \\cdot {1} }}$\n'
			padrao3 = '\\part ${0} + \\barra{{ {0} \\cdot {1} }}$\n'

			q=[]

			for i in range(qtd):

				letras = list(string.ascii_uppercase)
				letra1 = letras.pop(random.randint(0,len(letras)-1))
				letra2 = letras.pop(random.randint(0,len(letras)-1))
				letra3 = letras.pop(random.randint(0,len(letras)-1))
				
				while True:
					n=i%3
					if n==0:
						p=padrao1.format(letra1,letra2,letra3)
					elif n==1:
						p=padrao2.format(letra1,letra2,letra3)
					else:
						p=padrao3.format(letra1,letra2,letra3)

					if p not in q:
						q.append(p)
						prova.write(p)
						break

			prova.write(self.END_TAG_PARTS)				
			prova.close()

	def add_question_boolalg_distbool(self,qtd=10):

		with open(self.filename,"a") as prova:

			enunciado='\n\\question Simplifique as seguintes equações booleanas:\\\\ \n'
			enunciado+='\\textbf{{DICA}}: A primeira propriedade que deve ser aplicada é a \emph{{{0}}}\n'

			prova.write(enunciado.format('Distributividade Booleana'))
			prova.write(self.START_TAG_PARTS)

			padrao1 = '\\part ${0} + \\barra{{{1}}} \\cdot {0}$\n'
			padrao2 = '\\part $\\barra{{{0}}} + {0} \\cdot \\barra{{{1}}}$\n'

			q = []	
			for i in range(qtd):

				letras = list(string.ascii_uppercase)
				letra1 = letras.pop(random.randint(0,len(letras)-1))
				letra2 = letras.pop(random.randint(0,len(letras)-1))
	
				while True:
					if i%2:
						p = padrao1.format(letra1,letra2)
					else:
						p = padrao2.format(letra1,letra2)

					if p not in q:
						prova.write(p)
						q.append(p)
						break

			prova.write(self.END_TAG_PARTS)
			prova.close()

	def create_truth_table(self,equation,table={}):
		if table == {}:
			variables = [ l for l in equation if l in string.ascii_uppercase]
			print variables

			rest = set([ r for r in equation if r not in variables ])
			print rest

			accept = set(['(',')','+','&','~',' '])
			print accept

			if rest & accept == rest:
				print "OK"
				change = table_length = pow(2,len(variables))
				for var in variables:
					change/=2
					column = [ ]					
					for x in range(table_length):				
						if x==0:
							digit=0
						elif x%change==0:
							digit = 1 if digit == 0 else 0
						column.append(digit)
					table[var]=column
					print table[var]
				return self.create_truth_table(self,equation,table)
			else:
				raise (ValueError,"Invalid character:",rest, "\nMust be in", accept)
		else:
			if len(equation)==0:

			else:
				if '(' in equation:
					self.create_truth_table(self,equation.remove('('),table)
			

			
	def add_question_boolalg_distalg(self,qtd=10):

		with open(self.filename,"a") as prova:

			enunciado='\n\\question Simplifique as seguintes equações booleanas:\\\\ \n'
			enunciado+='\\textbf{{DICA}}: A primeira propriedade que deve ser aplicada é a \emph{{{0}}}\n'

			prova.write(enunciado.format('Distributividade Algébrica'))
			prova.write(self.START_TAG_PARTS)

			padroes = [] 

			padroes.append('$({0} + {1}) \\cdot ({0} + \\barra{{{1}}})$')
			padroes.append('$(\\barra{{{0}}} + \\barra{{{1}}}) \\cdot ({0}+\\barra{{{1}}})$')

			q = []
			for i in range(qtd):
				letras = list(string.ascii_uppercase)
	
				letra1 = letras.pop(random.randint(0,len(letras)-1))
				letra2 = letras.pop(random.randint(0,len(letras)-1))
				letra3 = letras.pop(random.randint(0,len(letras)-1))
	
				while True:
					pn = i%len(padroes)
					padrao = padroes[pn].format(letra1,letra2,letra3)
					
					p = '\\part ' + padrao + '\n'

					if p not in q:
						prova.write(p)
						q.append(p)
						break

			prova.write(self.END_TAG_PARTS)
				
			prova.close()

			


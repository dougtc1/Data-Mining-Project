from statistics import mean, pstdev, median
import functools
import os
from collections import defaultdict

#path = input("Ingrese el path completo de donde se encuentran los datos en .txt (con / al final de la última carpeta): ")

# Ejemplo de path: 
path = '/home/dougtc/Desktop/USB/mineria/proyecto/set-a/'
promedios = {}
promedios = defaultdict(lambda: [], promedios)
contador = 0

def cargarDataset(nombre):
	global contador
	data = {}
	data = defaultdict(lambda: [], data)
	faltantes = {}
	faltantes = defaultdict(lambda: [], faltantes)
	contadores = {}
	contadores = defaultdict(lambda: 0, contadores)
	lines = open(nombre, 'r').readlines()
	
	for line in lines:
		palabras = line.split(',')
		try:
			valor = float(palabras[2][:len(palabras[2]) - 1])
		except:
			continue
		
		if data['Gender'] == [-1.0] and palabras[1] == 'Weight' and valor > 99.0:
			data['Gender'] = [1.0]
		elif data['Gender'] == [-1.0] and palabras[1] == 'Weight' and valor  < 100.0:
			data['Gender'] = [0.0]

		if palabras[1] == 'NISysABP' and (valor < 50.0 or valor > 200.0):
			valor = -1.0
		elif palabras[1] == 'NIDiasABP' and (valor < 30.0 or valor > 120.0):
			valor = -1.0
		elif palabras[1] == 'Height' and valor > 0.0 and valor > 210.0 and ((valor < 160.0 and data['Gender'] == [1.0]) or (valor < 153.0 and data['Gender'] == [0.0])):
			valor = -1.0
		elif palabras[1] == 'Weight' and (valor < 45.0 or valor > 150.0):
			valor = -1.0
		elif palabras[1] == 'HR' and (valor < 30.0 or valor > 220.0): 
			valor = -1.0
		elif palabras[1] == 'PaCO2' and (valor < 20.0 or valor > 80.0):
			valor = -1.0
		elif palabras[1] == 'SaO2' and (valor < 55.0 or valor > 100.0):
			valor = -1.0
		elif palabras[1] == 'pH' and (valor < 6.8 or valor > 7.8):
			valor = -1.0
		elif palabras[1] == 'Temp' and (valor < 35.0 or valor > 41.0):
			valor = -1.0
		elif palabras[1] == 'TroponinT' and (valor > 0.1):
			valor = -1.0
		elif palabras[1] == 'WBC' and (valor > 25.0 or valor < 4.0):
			valor = -1.0

		if valor == -1.0 and palabras[1] != 'Gender':
			faltantes[palabras[1]].append(contadores[palabras[1]])
		else:
			promedios[palabras[1]].append(valor)

		contadores[palabras[1]] += 1
		data[palabras[1]].append(valor)

	return data, faltantes

def media(x, y):
	if y != - 1:
		return (y + x[0], x[1] + 1)
	else:
		return x

def procesarFaltantes(data):
	med = functools.reduce(media, data, (0, 0))
	med = med[0] / med[1]
	return med

def main():
	print("Se están leyendo los archivos de los pacientes.")
	pacientes = []
	outcomes = {}
	outcomes = defaultdict(lambda: [], outcomes)

	# Lectura del dataset
	for filename in os.listdir(path):
		pacientes.append(cargarDataset(path + filename))

	# Lectura de clases del dataset
	lines = open('Outcomes-a.txt', 'r').readlines()
	for line in lines:
		palabras = line.split(',')
		try:
			recordId = float(palabras[0])
		except:
			palabras[5] = palabras[5][:-1]
			aux = palabras[1:]
			continue
		palabras[5] = palabras[5][:-1]
		for i in palabras:
			outcomes[float(palabras[0])].append(i)
	
	# Calculo de promedios y creación de arreglo con strings de atributos
	for i in promedios:
		promedios[i] = mean(promedios[i])
	tmp = sorted(promedios, reverse=True)
	tmp.remove('RecordID')
	tmp.remove('ICUType')
	tmp.remove('Gender')
	tmp.remove('Age')
	tmp.remove('Height')
	tmp.remove('Weight')
	atributos = ['RecordID', 'ICUType', 'Gender', 'Age', 'Height', 'Weight']
	for i in range(len(tmp)):
		atributos.append(tmp.pop())
	for i in aux:
		atributos.append(i)
	
	# Archivo donde se va a escribir la dataset pre-procesada
	salida = open('datasetA.csv', 'w')
	linea = ''
	for i in atributos:
		linea += str(i) + ','
		
	salida.write(linea[:-1])
	salida.write('\n')
	linea = ''
	print("Se va a iniciar el tratamiento de los datos faltantes de los pacientes y la escritura al archivo datasetA.csv")
	# i es el paciente (Posicion 0: datos paciente, posicion 1: faltantes)
	for i in pacientes:
		# j es el nombre del atributo
		for j in i[0]:
			# Se verifica si el atributo j está en la lista de faltantes del paciente i
			if j in i[1]:
				# Se calcula la media del atributo j para ponerla como faltante al paciente i
				# En caso de que tenga un solo atributo (Ejemplo: Altura) y sea faltante, se toma el promedio de los pacientes
				try:
					media = procesarFaltantes(i[0][j])
				except:
					media = promedios[j]
				# k es la posicion faltante del atributo j en el paciente i
				for k in i[1][j]:
					i[0][j][k] = media
	
			# Calculo de estadísticos para series de tiempo y uso de atributos escalares
			if j == 'RecordID' or j == 'ICUType' or j == 'Gender' or j == 'Age' or j == 'Height':
				continue
			elif j == 'Weight':
				i[0][j] = [i[0][j][0]]
			else:
				minimo = min(i[0][j])
				maximo = max(i[0][j])
				mediana = median(i[0][j])
				primero = i[0][j][0]
				ultimo = i[0][j][len(i[0][j]) - 1]
				cantValores = len(i[0][j])
				# Sustitucion de valor en el diccionario del paciente i en el atributo j
				i[0][j] = [minimo, maximo, mediana, primero, ultimo, cantValores]
	
		# Aquí se escribe el paciente en el archivo .csv
		for x in atributos:
			n = len(i[0][x])
			for y in i[0][x]:
				linea += str(y) + ','

		for z in outcomes[i[0]['RecordID'][0]][1:]:
			linea += str(z) + ','
			
		salida.write(linea[:-1])
		salida.write('\n')
		linea = ''

if __name__ == '__main__':
	main()
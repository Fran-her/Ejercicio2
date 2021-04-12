import json
import requests
from bs4 import BeautifulSoup

class Compra:
	compras = []
	totalidad_productos = []
	posible_recompra = {}
	'''Debido a que esta clase recibe un diccionario y crea objetos "Compra", hice estas estructuras
	auxiliares propias de la clase para no perder referencia a cada instancia. "posible_recompra" es un
	diccionario que almacena como clave el nombre de cada producto y como valor la fecha de posible recompra.'''

	def __init__(self,transaccion_numero,fecha,productos):
		'''Este metodo inicializa los atributos del objeto Compra creado.
		Idealmente los datos almacenados de "transaccion_numero" y "fecha" son cadenas de
		caracteres, mientras que "productos" es una lista de cadenas de caracteres.'''
		self.transaccion_numero = transaccion_numero
		self.fecha = fecha
		self.productos = productos

	@classmethod
	def procesar_diccionario(cls,dic):
		'''Este metodo recibe un diccionario, crea objetos "Compra" y los adjunta
		a la lista "compras" propia de la clase.'''
		for i in dic["customer"]["purchases"]:
			transaccion_numero = i["number"]
			fecha = i["date"]
			productos = []
			for j in i["products"]:
				productos.append(j["name"])
				if not j["name"] in cls.totalidad_productos:
					cls.totalidad_productos.append(j["name"])
			cls.compras.append(Compra(transaccion_numero,fecha,productos))

	@classmethod
	def calculo_recompra_productos(cls):
		'''Este metodo analiza la lista "totalidad_productos" propia de la clase, recorre la
		lista "compras" propia de la clase, compara los elementos desde	la fecha mas reciente
		hasta encontrar dos fechas para un mismo producto, calcula cuando sera la posible recompra
		de ese producto y almacena ese dato como valor del diccionario "posible_recompra" propio de la clase.
		Por ultimo, de ser calculable, muestra en pantalla la posible fecha de recompra para el producto.'''
		for i in cls.totalidad_productos:
			fecha_2 = False
			fecha_1 = False
			for j in range(len(cls.compras)-1,-1,-1):
				for k in cls.compras[j].productos:
					if k == i and fecha_2 == False:
						fecha_2 = cls.compras[j].fecha
					elif k == i and fecha_2 != False:
						fecha_1 = cls.compras[j].fecha
				if fecha_1 != False and fecha_2 != False:
					break
			if fecha_1 != False and fecha_2 != False:
				#Aca pense en utilizar la libreria datetime de Python, pero alteraba el formato al hacer "deltatime()"
				anio_2, mes_2, dia_2 = fecha_2.split('-')
				anio_1, mes_1, dia_1 = fecha_1.split('-')
				anio_recompra = str(int(anio_2)+int(anio_2)-int(anio_1))
				mes_recompra = str(int(mes_2)+int(mes_2)-int(mes_1))
				dia_recompra = str(int(dia_2)+int(dia_2)-int(dia_1))
				if len(mes_recompra) == 1:
					mes_recompra = '0'+ mes_recompra
				if len(dia_recompra) == 1:
					dia_recompra = '0'+ dia_recompra
				cls.posible_recompra[i] = "{}-{}-{}".format(anio_recompra,mes_recompra,dia_recompra)
				print("La proxima compra del producto {} sera el {}-{}-{}".format(i,anio_recompra,mes_recompra,dia_recompra))
		print()

class Procesador_url:

	def __init__(self,url):
		'''Este metodo inicializa los atributos del objeto Procesador_url creado.
		Almacena para cada instancia, un url y el diccionario que se obtiene luego
		de procesar dicho url.'''
		self.url = url
		self.diccionario = Procesador_url.obtener_diccionario_json(self.url)

	@staticmethod
	def obtener_diccionario_json(url):
		'''Este metodo recibe un url, obtiene la pagina web, decodifica el contenido, busca
		el fragmento de formato JSON, lo cambia a un diccionario de Python y lo devuelve.'''
		#En particular tuve problemas con el manejo de HTML<Tags>. Comprendi por que utilizan PHP.
		response = requests.get(url)
		soup = BeautifulSoup(response.content,'html.parser')
		script = soup.find_all('p')[1].text.strip()
		script += "]}]}}"							#Este renglon es hardcodeo porque no funcionaron otras alternativas.
		diccionario = json.loads(script)
		return diccionario

#Tests Unitarios
'''En estas pruebas unitarias para un url dado, creo un objeto Procesador_url que obtiene
un diccionario para manejar los datos de fecha y productos. La clase "Compra" procesa el
diccionario, obtiene una lista de compras y un diccionario de posibles recompras.
Verifico que las fechas de recompra sean congruentes.
Luego creo dos instancias nuevas de "Compra", las agrego a la lista "compras" de la clase y
calculo nuevamente la recompra de los productos. Verifico nuevamente que las fechas de
recompra sean coherentes.'''
def main():
	url = "https://blankslate.io/?note=454370"
	proc = Procesador_url(url)
	Compra.procesar_diccionario(proc.diccionario)
	Compra.calculo_recompra_productos()
	assert(Compra.posible_recompra["Cat Chow 1KG"] == "2020-04-01")
	assert(Compra.posible_recompra["Tidy Cats 2KG"] == "2020-05-01")

	Compra.compras.append(Compra("B001-002310","2020-03-15",["Royal canin cat ultra light pouch"]))
	Compra.compras.append(Compra("B001-002311","2020-04-01",["Cat Chow 1KG"]))
	Compra.calculo_recompra_productos()
	assert(Compra.posible_recompra["Royal canin cat ultra light pouch"] == "2020-05-15")
	assert(Compra.posible_recompra["Cat Chow 1KG"] == "2020-05-01")

main()
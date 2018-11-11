import requests
import sys
import os
import csv
from lxml import html


def download(url):
	"""Obtiene el código HTML correspondiente a una determinada URL
		:param url: URL desde la que se obtiene el código fuente.
	"""
	r = requests.get(url)
	if r.status_code != 200:
		sys.stderr.write("! Error {} descargando url {}\n".format(r.status_code, url))
		return None

	return r

def get_categories(page):
	# Obtenemos estructuras XML del contenido de la página
	tree = html.fromstring(page.content)
	# Con xpath obtenemos los enlaces a href de la página
	xpath_string = '//a/@href'
	results = tree.xpath(xpath_string)
	return results

def remove_duplicates(results):
	"""Elimina duplicados de la lista, dejando solamente valores únicos.
	"""
	unique_results=[]
	for item in results:
		if not item in unique_results:
			unique_results.append(item)
	return unique_results

if __name__ == '__main__':

	url = "https://www.todocoleccion.net/"

	page = download(url)
	if page:
		#sys.stdout.write("\n\n1) Download text from {}\n".format(url))
		#sys.stdout.write(page.text[:200])

		currentDir = os.path.dirname(__file__)
		filename = "ajulianb_PRAC1.csv"
		filePath = os.path.join(currentDir, filename)
		pattern='/s/'
		aux_list=[]
		
		results=get_categories(page)
		
		unique_results=remove_duplicates(results)
		with open(filePath, 'w', newline='') as csvFile:
			writer = csv.writer(csvFile)
			#Iteramos sobre los enlaces obtenidos para obtener los que corresponden a categorías de productos
			for item in unique_results:
				if item.find('/s/')!=-1 and item.find('https'):
					#Escribimos la categoría en el csv
					writer.writerow([item.replace('/s/','s/')])
					#Para cada categoría obtenida, generamos la url para obtener sus subcategorías
					category=''.join(item.replace('/s/','s/'))
					url2=url+category
					#Descargamos la URL correspondiente a la categoría para obtener sus subcategorías
					page_cat = download(url2)
					if page_cat:
						category_results=get_categories(page_cat)
						cat_unique_results=remove_duplicates(category_results)
						for cat_item in cat_unique_results:
							if cat_item.find('/s/')!=-1 and cat_item.find('https'):
								#Limpiamos la subcategoría obtenida para quedarnos con valores únicos
								start = cat_item.find('/s/') + 3
								end = cat_item.find('?', start)
								try:
									aux_list.append(cat_item[start:end])
									aux_list=remove_duplicates(aux_list)
									for aux_item in aux_list:
										#Escribimos la categoría en el csv
										writer.writerow([aux_item])
								except AttributeError:
									#do nothing
									sys.stderr.write("! Error extrayendo categoría {}\n".format(cat_item))
	else:
		sys.stdout.write("Sin resultados.")
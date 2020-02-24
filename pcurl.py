import pycurl
try:
	from StringIO import StringIO
except:
	from io import StringIO

from xml.dom import minidom
from os import remove
from lxml import etree

emisor = receptor = total = uuid = xml = ""
io = StringIO()

debug = True

try:
	ruta_xml = raw_input("Ruta XML: ")
except:
	ruta_xml = input('Ruta XML:')
file = etree.parse(ruta_xml)

#from pdb import set_trace; set_trace();

emisor = file.xpath('//cfdi:Emisor/@Rfc', namespaces={'cfdi': 'http://www.sat.gob.mx/cfd/3'})
receptor = file.xpath('//cfdi:Receptor/@Rfc', namespaces={'cfdi': "http://www.sat.gob.mx/cfd/3"})
total = file.xpath('//@Total')
uuid = file.xpath('//tfd:TimbreFiscalDigital/@UUID', namespaces={'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'})
xml = "?re=" + emisor[0] + "&amp;rr=" + receptor[0] + "&amp;tt=" + total[0] + "&amp;id=" + uuid[0]
if debug:
	url = "https://pruebacfdiconsultaqr.cloudapp.net/ConsultaCFDIService.svc"
else:
	url = "https://consultaqr.facturaelectronica.sat.gob.mx/ConsultaCFDIService.svc"
soap = """
		<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/">
			<soapenv:Body>
				<tem:Consulta>
					<tem:expresionImpresa>""" + str(xml) + """</tem:expresionImpresa>
				</tem:Consulta>
			</soapenv:Body>
		</soapenv:Envelope>
		""" 
headers = ['Host: consultaqr.facturaelectronica.sat.gob.mx',
       'POST: https://pruebacfdiconsultaqr.cloudapp.net/ConsultaCFDIService.svc HTTP/1.1' if debug else 'POST: https://consultaqr.facturaelectronica.sat.gob.mx/ConsultaCFDIService.svc HTTP/1.1',
       'SOAPAction: http://tempuri.org/IConsultaCFDIService/Consulta',
       'Content-Type: text/xml; charset=utf-8',
       'Connection: keep-Alive',
       'Content-Length: ' + str(len(soap)) ,]

c = pycurl.Curl()
c.setopt(c.URL, url)
c.setopt(c.WRITEFUNCTION, io.write)
c.setopt(c.POST, 1)
c.setopt(c.POSTFIELDS, soap)
c.setopt(c.HTTPHEADER, headers)
c.setopt(c.SSL_VERIFYPEER, 0)
c.setopt(c.SSL_VERIFYHOST, 2)

try:
	c.perform()
	response = io.getvalue()

	file = open("content.xml", "w")
	file.write(response)
	file.close()

	file = open("content.xml", "r")
	doc = etree.parse(file)
	print(doc.xpath('//a:CodigoEstatus/text()', namespaces={'a': 'http://schemas.datacontract.org/2004/07/Sat.Cfdi.Negocio.ConsultaCfdi.Servicio'}))
except pycurl.error as e:
	print(e)
finally:
	c.close()
	file.close()
	remove("content.xml")

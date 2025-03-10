from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_der_x509_certificate

from lxml import etree
import base64

"""
En este método se carga la llave privada desde el archivo .key
sacado del SAT (proveen estos archivos para hacer pruebas como
esta). Igualmente, se require la contraseña de la clave privada
que también el SAT especifica. 

En el método se lee el archivo de la clave, luego se convierte
a bytes y se realizan las operaciones criptográficas de la 
librería cryptography.
"""
def load_private_key(key_path, password):
    with open(key_path, "rb") as key_file:
        clave_privada = serialization.load_der_private_key(
            key_file.read(), password=password.encode(), backend=default_backend()
        )
    return clave_privada

"""
El método load certificate ahora carga el certificado del
archivo .cer
"""
def load_certificate(cer_path):
    # Carga el certificado desde un archivo .cer
    with open(cer_path, "rb") as cer_file:
        cert = load_der_x509_certificate(cer_file.read())
    return cert

"""
Tras conseguir la llave y hacerle el encode a bytes se genera el sello
que se agrega a la nueva versión del xml. Además de esta clave, se 
necesita la cadena original. 

Esta cadena original se consigue usando un formato xslt provisto
por el SAT y el XML original. Esa cadena condensa los datos de 
la supuesta factura. Usando esta información se genera el sello que
se insertará en el xml. 

Este sello se codifica en base64 y se hace una cadena.
"""
def generate_sello(clave_privada, cadena_original):
    # Firma la cadena original con la clave privada
    signature = clave_privada.sign(
        cadena_original.encode(),
        padding.PKCS1v15(),
        hashes.SHA256(),
    )
    return base64.b64encode(signature).decode()


"""
Finalmente, se especifican las rutas de archivos, password, la
cadena original y se llaman los métodos para generar el sello. 
Una vez generado el sello digital, este se añade al xml con el 
último método.
"""
# Rutas de los archivos 
cer_path = "tu_certificado.cer"
key_path = "tu_llave.KEY"
password = "12345678a"

# Cargar llave y certificado
clave_privada = load_private_key(key_path, password)
cert = load_certificate(cer_path)

# Cadena original generada con un generador usando un XSLT del SAT y el xml que vamos a firmar (el archivo)
cadena_original = "||4.0|A|12345|2024-03-05T12:00:00|01||Contado|1000.00|MXN|1160.00|I||PUE|64000|AAA010101AAA|EMPRESA EMISORA S.A. DE C.V.|601|BBB020202BBB|CLIENTE EJEMPLO|||G03|01010101|1|H87|Producto de prueba|1000.00|1000.00||1000.00|002|Tasa|0.160000|160.00|1000.00|002|Tasa|0.160000|160.00|160.00||"

# Generar el sello
sello_digital = generate_sello(clave_privada, cadena_original)

print(f"Sello digital generado:\n{sello_digital}")

def insert_sello_in_xml(xml_path, sello):
    # Inserta el sello en el CFDI
    tree = etree.parse(xml_path)
    root = tree.getroot()
    root.attrib["Sello"] = sello
    tree.write("cfdi_firmado.xml", xml_declaration=True, encoding="UTF-8")

xml_path = "cfdi.xml"
insert_sello_in_xml(xml_path, sello_digital)

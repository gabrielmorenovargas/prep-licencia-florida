import boto3
import json
import os

# Detectar el endpoint inyectado por Docker
endpoint_url = os.environ.get('DYNAMODB_URL', 'http://localhost:8000')
print(f"🔌 Conectando a DynamoDB en el endpoint: {endpoint_url}")

# Conexión estándar de AWS alineada con tus llaves alfanuméricas
session = boto3.Session(
    aws_access_key_id='mockkey2026',
    aws_secret_access_key='mockkey2026',
    region_name='us-east-1'
)
dynamodb = session.resource('dynamodb', endpoint_url=endpoint_url)

def cargar_y_unificar_jsons():
    preguntas_unificadas = []
    archivos = ['preguntas_parte1.json', 'preguntas_parte2.json']
    
    for archivo in archivos:
        if os.path.exists(archivo):
            print(f"📖 Leyendo datos de {archivo}...")
            with open(archivo, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                preguntas_unificadas.extend(datos)
        else:
            print(f"⚠️ Advertencia: No se encontró el archivo '{archivo}', se omitirá.")
            
    return preguntas_unificadas

def inicializar_base_de_datos():
    print("⏳ Comprobando estado de la tabla 'FloridaDrive_Preguntas'...")
    try:
        tabla = dynamodb.create_table(
            TableName='FloridaDrive_Preguntas',
            KeySchema=[{'AttributeName': 'PK', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'PK', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 10, 'WriteCapacityUnits': 10}
        )
        tabla.wait_until_exists()
        print("✅ Tabla NoSQL creada exitosamente desde cero.")
    except Exception as e:
        if "ResourceInUseException" in str(e):
            print("ℹ️ La tabla ya existe en el contenedor. Actualizando banco de preguntas...")
            tabla = dynamodb.Table('FloridaDrive_Preguntas')
        else:
            print(f"❌ Error crítico de AWS: {e}")
            return

    # Obtener el lote unificado de las 60 preguntas
    banco_total = cargar_y_unificar_jsons()
    
    if not banco_total:
        print("❌ Error: No hay preguntas disponibles para insertar. Verifica los archivos JSON.")
        return

    print(f"📥 Insertando {len(banco_total)} preguntas en el motor NoSQL de Docker...")
    
    # Inyección masiva y segura
    with tabla.batch_writer() as batch:
        for nuevo_id, q in enumerate(banco_total, start=1):
            batch.put_item(Item={
                'PK': f"PREGUNTA#{nuevo_id}",
                'id': nuevo_id,
                'pregunta': q['pregunta'],
                'opciones': q['opciones'],
                'respuesta_correcta': q['respuesta_correcta'],
                'explicacion': q.get('explicacion', 'Consulte el manual oficial de conducción de Florida.')
            })
            
    print(f"🚀 ¡Base de datos local sincronizada perfectamente con {len(banco_total)} preguntas!")

if __name__ == "__main__":
    inicializar_base_de_datos()

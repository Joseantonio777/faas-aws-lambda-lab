import json
import boto3

# Inicializar el cliente de AWS Lambda
lambda_client = boto3.client('lambda')

def lambda_handler(event, context):
    """
    Función Productora:
    Recibe o genera datos y los envía a la función ConsumidorFuncion vía boto3.
    """
    # 1. Preparar la estructura de datos a enviar
    data = {
        'message': 'Hola desde Productor',
        'value': 42
    }
    
    # 2. Invocar de manera síncrona (RequestResponse) a la función ConsumidorFuncion
    response = lambda_client.invoke(
        FunctionName='ConsumidorFuncion',
        InvocationType='RequestResponse',  # Esperar respuesta
        Payload=json.dumps(data)
    )
    
    # 3. Leer y decodificar el Payload de respuesta del consumidor
    response_payload = json.loads(response['Payload'].read())
    
    # 4. Retornar el estado final agregando las respuestas de ambos componentes
    return {
        'statusCode': 200,
        'body': json.dumps({
            'ProducerResponse': 'Data enviada a consumidor',
            'ConsumerResponse': response_payload
        })
    }

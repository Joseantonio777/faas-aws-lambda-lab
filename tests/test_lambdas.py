import unittest
from unittest.mock import MagicMock, patch
import json
import sys
import os

# Insertar el directorio src en el path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Mockear boto3 en sys.modules si no está instalado en el entorno local
if 'boto3' not in sys.modules:
    mock_boto3 = MagicMock()
    sys.modules['boto3'] = mock_boto3

from consumidor_funcion import lambda_handler as consumidor_handler

class TestLambdaFunctions(unittest.TestCase):

    def test_consumidor_funcion_exito(self):
        event = {'message': 'Test Message', 'value': 21}
        response = consumidor_handler(event, None)
        
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['ConsumerMessage'], 'Test Message')
        self.assertEqual(body['ProcessedValue'], 42)

    def test_consumidor_funcion_valores_defecto(self):
        event = {}
        response = consumidor_handler(event, None)
        
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['ConsumerMessage'], 'Ningun mensaje recibido')
        self.assertEqual(body['ProcessedValue'], 0)

    def test_productor_funcion(self):
        # Mock del cliente Lambda
        mock_lambda_client = MagicMock()
        sys.modules['boto3'].client.return_value = mock_lambda_client
        
        # Simular la respuesta del consumidor
        consumer_payload = {
            'statusCode': 200,
            'body': json.dumps({
                'ConsumerMessage': 'Hola desde Productor',
                'ProcessedValue': 84
            })
        }
        
        mock_payload_stream = MagicMock()
        mock_payload_stream.read.return_value = json.dumps(consumer_payload).encode('utf-8')
        mock_lambda_client.invoke.return_value = {'Payload': mock_payload_stream}
        
        # Importar y ejecutar el productor
        from productor_funcion import lambda_handler as productor_handler
        response = productor_handler({}, None)
        
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['ProducerResponse'], 'Data enviada a consumidor')
        self.assertEqual(body['ConsumerResponse']['statusCode'], 200)

if __name__ == '__main__':
    unittest.main()


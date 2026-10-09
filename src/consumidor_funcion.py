import json

def lambda_handler(event, context):
    """
    Función Consumidora:
    Procesa los datos recibidos del evento de entrada y aplica una transformación matemática simple.
    """
    # 1. Obtener valores con valores por defecto de resguardo
    message = event.get('message', 'Ningun mensaje recibido')
    value = event.get('value', 0)
    
    # 2. Operación de procesamiento (multiplicar valor por 2)
    result = value * 2
    
    # 3. Retorno del resultado en formato JSON
    return {
        'statusCode': 200,
        'body': json.dumps({
            'ConsumerMessage': message,
            'ProcessedValue': result
        })
    }

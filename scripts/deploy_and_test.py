import sys
import os
import json
import zipfile
import io

# Configurar stdout para UTF-8 si es posible
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Recibir credenciales por variables de entorno o ingresar manualmente
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "YOUR_AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "YOUR_AWS_SECRET_ACCESS_KEY")
AWS_SESSION_TOKEN = os.environ.get("AWS_SESSION_TOKEN", "YOUR_AWS_SESSION_TOKEN")
REGION_NAME = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")


import boto3

def create_zip_bytes(py_file_path):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        with open(py_file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        zf.writestr('lambda_function.py', code)
    zip_buffer.seek(0)
    return zip_buffer.read()

def main():
    print("Conectando con AWS...")
    
    # Intentar obtener la cuenta actual para obtener el ARN del LabRole
    sts = boto3.client(
        'sts',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        aws_session_token=AWS_SESSION_TOKEN,
        region_name=REGION_NAME
    )
    
    try:
        identity = sts.get_caller_identity()
        account_id = identity['Account']
        print(f"[OK] Autenticado exitosamente en AWS Account: {account_id}")
    except Exception as e:
        print(f"[ERROR] Error de autenticacion en AWS: {e}")
        return

    # Probar primero en us-east-1 (Norte de Virginia) y si no en us-west-2
    regions_to_try = ["us-east-1", "us-west-2", REGION_NAME]
    
    role_arn = f"arn:aws:iam::{account_id}:role/LabRole"
    
    active_region = None
    active_lambda_cli = None
    
    for reg in regions_to_try:
        try:
            print(f"\nProbando cliente Lambda en region: {reg}")
            lambda_cli = boto3.client(
                'lambda',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                aws_session_token=AWS_SESSION_TOKEN,
                region_name=reg
            )
            # Listar funciones para verificar conexion y region correcta
            res = lambda_cli.list_functions()
            print(f"[OK] Conexion exitosa a Lambda en {reg}. Funciones encontradas: {len(res.get('Functions', []))}")
            active_region = reg
            active_lambda_cli = lambda_cli
            break
        except Exception as e:
            print(f"[WARN] No se pudo listar en {reg}: {e}")
            continue
            
    if not active_lambda_cli:
        print("[ERROR] No se pudo conectar a Lambda en ninguna region probada.")
        return

    # Deploy de ConsumidorFuncion
    consumidor_zip = create_zip_bytes("src/consumidor_funcion.py")
    try:
        print("\nDesplegando/Actualizando 'ConsumidorFuncion'...")
        try:
            active_lambda_cli.get_function(FunctionName='ConsumidorFuncion')
            active_lambda_cli.update_function_code(
                FunctionName='ConsumidorFuncion',
                ZipFile=consumidor_zip
            )
            print("[OK] 'ConsumidorFuncion' actualizada exitosamente.")
        except active_lambda_cli.exceptions.ResourceNotFoundException:
            active_lambda_cli.create_function(
                FunctionName='ConsumidorFuncion',
                Runtime='python3.12',
                Role=role_arn,
                Handler='lambda_function.lambda_handler',
                Code={'ZipFile': consumidor_zip},
                Description='Funcion Consumidora para Laboratorio FaaS'
            )
            print("[OK] 'ConsumidorFuncion' creada exitosamente.")
    except Exception as e:
        print(f"[ERROR] Error al desplegar ConsumidorFuncion: {e}")

    # Deploy de ProductorFuncion
    productor_zip = create_zip_bytes("src/productor_funcion.py")
    try:
        print("\nDesplegando/Actualizando 'ProductorFuncion'...")
        try:
            active_lambda_cli.get_function(FunctionName='ProductorFuncion')
            active_lambda_cli.update_function_code(
                FunctionName='ProductorFuncion',
                ZipFile=productor_zip
            )
            print("[OK] 'ProductorFuncion' actualizada exitosamente.")
        except active_lambda_cli.exceptions.ResourceNotFoundException:
            active_lambda_cli.create_function(
                FunctionName='ProductorFuncion',
                Runtime='python3.12',
                Role=role_arn,
                Handler='lambda_function.lambda_handler',
                Code={'ZipFile': productor_zip},
                Description='Funcion Productora para Laboratorio FaaS'
            )
            print("[OK] 'ProductorFuncion' creada exitosamente.")
    except Exception as e:
        print(f"[ERROR] Error al desplegar ProductorFuncion: {e}")

    # Esperar estado Active de ambas funciones
    def wait_for_active(name):
        print(f"Esperando a que '{name}' pase a estado Active...")
        waiter = active_lambda_cli.get_waiter('function_active')
        waiter.wait(FunctionName=name)
        print(f"[OK] '{name}' esta activa y lista.")

    wait_for_active('ConsumidorFuncion')
    wait_for_active('ProductorFuncion')

    # Ejecutar/Invocar ProductorFuncion
    print("\nEjecutando prueba de invocacion en ProductorFuncion...")
    try:
        invoke_res = active_lambda_cli.invoke(
            FunctionName='ProductorFuncion',
            InvocationType='RequestResponse'
        )
        payload_raw = invoke_res['Payload'].read()
        payload = json.loads(payload_raw)
        print("\n================ RESULTADO DE LA EJECUCION AWS ================")
        print(json.dumps(payload, indent=2))
        print("===============================================================")
    except Exception as e:
        print(f"[ERROR] Error al invocar ProductorFuncion: {e}")


if __name__ == "__main__":
    main()


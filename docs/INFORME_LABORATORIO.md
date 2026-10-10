# INFORME DE LABORATORIO: INFRAESTRUCTURA FaaS (AWS LAMBDA)

**Asignatura:** Infraestructura de aplicaciones II (INY1106)  
**Experiencia de Aprendizaje:** EA2: Infraestructura Serverless  
**Indicador de Logro:** IL2.1  
**Modalidad de Trabajo:** Parejas  

---

## 1. Portada

* **Integrantes:** 
  * [Nombre Integrante 1]
  * [Nombre Integrante 2]
* **Docente:** [Nombre del Docente]
* **Institución:** Duoc UC / AWS Academy
* **Fecha:** 9 de octubre de 2026

---

## 2. Introducción

En el ámbito de la computación en la nube y las arquitecturas modernas, el modelo **Serverless** (sin servidor) ha transformado la manera en que se despliegan y gestionan las aplicaciones. En particular, la arquitectura de **Función como Servicio (FaaS)** permite ejecutar bloques de código específicos en respuesta a eventos sin la necesidad de aprovisionar, administrar o escalar servidores subyacentes.

AWS Lambda es uno de los servicios FaaS más consolidados del mercado. En este laboratorio, se aborda la implementación de un patrón de comunicación sincrónica entre dos funciones Lambda (`ProductorFuncion` y `ConsumidorFuncion`). Este ejercicio permite comprender el funcionamiento de la invocación programática mediante el SDK de AWS (`boto3` en Python 3.12) y el rol de los permisos IAM (`LabRole`) en la interconexión de servicios Serverless.

---

## 3. Proceso de Implementación y Configuración

### 3.1 Creación de la Función Consumidora (`ConsumidorFuncion`)
1. En la consola de AWS Lambda, se seleccionó **Crear una función** -> **Crear desde cero**.
2. **Nombre de la función:** `ConsumidorFuncion`.
3. **Runtime:** Python 3.12.
4. **Rol de ejecución:** Se asignó el rol existente **`LabRole`** provisto por AWS Academy.
5. **Código fuente:** Se implementó la lógica de procesamiento que toma los parámetros `message` y `value`, retornando el mensaje y el doble del valor recibido.

```python
import json

def lambda_handler(event, context):
    message = event.get('message', 'Ningun mensaje recibido')
    value = event.get('value', 0)
    result = value * 2
    return {
        'statusCode': 200,
        'body': json.dumps({
            'ConsumerMessage': message,
            'ProcessedValue': result
        })
    }
```

### 3.2 Creación de la Función Productora (`ProductorFuncion`)
1. Se creó la función `ProductorFuncion` utilizando el runtime **Python 3.12** y el rol **`LabRole`**.
2. **Código fuente:** Se utilizó el cliente `boto3` para invocar sincrónicamente a `ConsumidorFuncion` enviando una carga útil en formato JSON.

```python
import json
import boto3

lambda_client = boto3.client('lambda')

def lambda_handler(event, context):
    data = {
        'message': 'Hola desde Productor',
        'value': 42
    }
    response = lambda_client.invoke(
        FunctionName='ConsumidorFuncion',
        InvocationType='RequestResponse',
        Payload=json.dumps(data)
    )
    response_payload = json.loads(response['Payload'].read())
    return {
        'statusCode': 200,
        'body': json.dumps({
            'ProducerResponse': 'Data enviada a consumidor',
            'ConsumerResponse': response_payload
        })
    }
```

---

## 4. Interacción entre Funciones Lambda y Evidencias de Prueba

### 4.1 Invocación y Prueba de Integración
1. Se configuró un evento de prueba estándar en la consola de AWS Lambda para `ProductorFuncion`.
2. Al ejecutar la prueba, `ProductorFuncion` envió los datos `{'message': 'Hola desde Productor', 'value': 42}` a `ConsumidorFuncion`.
3. `ConsumidorFuncion` procesó el valor ($42 \times 2 = 84$) y devolvió la respuesta estructurada a `ProductorFuncion`.

### 4.2 Resultado Obtenido de la Ejecución Real en AWS (us-east-1)

**AWS Account:** `935751870067`  
**Estado:** Invocación Exitosa (`statusCode: 200`)  

```json
{
  "statusCode": 200,
  "body": "{\"ProducerResponse\": \"Data enviada a consumidor\", \"ConsumerResponse\": {\"statusCode\": 200, \"body\": \"{\\\"ConsumerMessage\\\": \\\"Hola desde Productor\\\", \\\"ProcessedValue\\\": 84}\"}}"
}
```

#### Desglose de Respuestas:
1. **Productor (`ProducerResponse`):** Confirmación de envío `"Data enviada a consumidor"`.
2. **Consumidor (`ConsumerResponse`):**
   - **`ConsumerMessage`:** `"Hola desde Productor"` (Mensaje recepcionado).
   - **`ProcessedValue`:** `84` (Valor transformado: $42 \times 2 = 84$).

---

## 5. Conclusiones

1. **Modularidad y Desacoplamiento:** La arquitectura serverless permite desacoplar responsabilidades. Al separar la producción de datos del procesamiento de los mismos, se facilita el mantenimiento, testing y escalabilidad independiente de cada componente.
2. **Gestión de Permisos (IAM):** Para que una función Lambda pueda invocar a otra, es indispensable contar con permisos adecuados (como `lambda:InvokeFunction`). En el entorno de AWS Academy, el rol preconfigurado `LabRole` otorga estos privilegios de forma transparente.
3. **Invocación Sincrónica vs Asincrónica:** El parámetro `InvocationType='RequestResponse'` permite llamadas sincrónicas en tiempo real. En escenarios donde no se requiere respuesta inmediata, se puede optar por `InvocationType='Event'` (asincrónico) para liberar recursos rápidamente.
4. **Desafíos Resueltos:** Durante la actividad se comprendió el manejo del stream de respuesta de `boto3` (`Payload.read()`), el ciclo de vida del estado de la función (`Pending` -> `Active`), y la serialización/deserialización doble de JSON en respuestas compuestas.


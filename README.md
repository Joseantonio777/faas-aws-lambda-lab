# Laboratorio Infraestructura FaaS - AWS Lambda

Repositorio del laboratorio práctico **"EA2: Infraestructura Serverless"** para la asignatura *Infraestructura de Aplicaciones II* (INY1106).

## 🚀 Descripción

Este proyecto implementa un patrón de arquitectura Serverless en **AWS Lambda** utilizando Python 3.12 y el SDK `boto3`. Demuestra la invocación sincrónica de una función Lambda consumidora desde una función Lambda productora.

## 📁 Estructura del Proyecto

```
faas-aws-lambda-lab/
├── src/
│   ├── productor_funcion.py    # Código de ProductorFuncion (invoca a Consumidor)
│   └── consumidor_funcion.py   # Código de ConsumidorFuncion (procesa datos)
├── tests/
│   └── test_lambdas.py         # Pruebas unitarias locales (mock con unittest)
├── docs/
│   └── INFORME_LABORATORIO.md  # Informe de la actividad estructurado
└── README.md                   # Documentación principal
```

## 🧪 Pruebas Locales

Para ejecutar el conjunto de pruebas unitarias locales sin necesidad de desplegar inmediatamente en AWS:

```bash
python -m unittest discover -s tests
```

## ☁️ Despliegue en AWS Academy

1. Crear la función `ConsumidorFuncion` en AWS Lambda con runtime **Python 3.12** y rol **LabRole**. Copiar el contenido de `src/consumidor_funcion.py`.
2. Crear la función `ProductorFuncion` en AWS Lambda con runtime **Python 3.12** y rol **LabRole**. Copiar el contenido de `src/productor_funcion.py`.
3. Probar `ProductorFuncion` mediante el botón **Test** en la consola de AWS.

## 📄 Informe

El documento completo con la introducción, configuración, capturas y conclusiones se encuentra en [`docs/INFORME_LABORATORIO.md`](docs/INFORME_LABORATORIO.md).

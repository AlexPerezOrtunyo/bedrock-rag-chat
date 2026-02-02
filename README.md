# bedrock-rag-chat
PAC: Asistente Inmobiliario Inteligente con RAG y AWS Bedrock

# 🧠 Bedrock RAG Chat: Inteligencia Artificial sobre Documentos Propios

Este repositorio contiene una implementación avanzada de **RAG (Retrieval-Augmented Generation)** utilizando **Amazon Bedrock**. El sistema permite "conversar" con archivos locales (PDF, TXT, MD) utilizando modelos de lenguaje de última generación sin comprometer la privacidad de los datos.

## 🌟 Características

- **Arquitectura RAG:** Recuperación de contexto en tiempo real para respuestas sin alucinaciones.
- **Multi-Model Support:** Compatible con Claude 3 (Haiku/Sonnet), Llama 3 y Amazon Titan.
- **Embeddings de AWS:** Uso de `amazon.titan-embed-text-v1` para vectorización semántica.
- **Memoria de Conversación:** Capacidad para recordar el contexto previo del chat.
- **Persistencia Vectorial:** Almacenamiento local de índices para evitar re-procesar documentos.

## 🏗️ Arquitectura del Sistema

1. **Ingesta:** Los documentos se dividen en fragmentos (*chunks*) usando `RecursiveCharacterTextSplitter`.
2. **Vectorización:** Los fragmentos se convierten en vectores numéricos vía Amazon Bedrock.
3. **Almacenamiento:** Se guardan en una base de datos vectorial (FAISS/ChromaDB).
4. **Consulta:** El sistema busca los fragmentos más relevantes a la pregunta del usuario.
5. **Generación:** El LLM recibe el contexto y genera una respuesta precisa.

## 📋 Requisitos Técnicos

- **Python:** 3.9 o superior.
- **Boto3:** SDK de AWS para Python.
- **LangChain:** Framework para orquestación de LLMs.
- **Permisos AWS:** Usuario IAM con política `AmazonBedrockFullAccess`.

## 🛠️ Configuración e Instalación

### 1. Clonar y Preparar Entorno
```bash
git clone [https://github.com/tu-usuario/bedrock-rag-chat.git](https://github.com/tu-usuario/bedrock-rag-chat.git)
cd bedrock-rag-chat
python -m venv venv
# Activar entorno
# Windows: .\venv\Scripts\activate | Linux: source venv/bin/activate

2. Variables de Entorno
Crea un archivo .env con la siguiente estructura:

AWS_ACCESS_KEY_ID=tu_clave_de_acceso
AWS_SECRET_ACCESS_KEY=tu_clave_secreta
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
3. Instalación de Librerías
Bash

pip install boto3 langchain langchain-community pypdf faiss-cpu python-dotenv

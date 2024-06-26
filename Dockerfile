# Usa una imagen base de Python
FROM python:3.11

# Configura el directorio de trabajo
WORKDIR /app

# Copia los archivos de tu proyecto al contenedor
COPY . /app

# Instala las dependencias de tu proyecto
RUN pip install -r requirements.txt

RUN alembic revision --autogenerate -m "Initial migration"

# Expón el puerto en el que se ejecutará tu aplicación FastAPI
EXPOSE 8000

# Comando para ejecutar tu aplicación FastAPI
CMD ["uvicorn", "api.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

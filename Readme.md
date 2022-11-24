# API Evaluacion KSP

## Description :book:
En este repositorio se encuentra la API REST, desarrollada con flask, para la evaluación tencnica de la empresa KSP.
El proyecto cuenta con un Make faile con comandos muy utiles.

## Installation :hammer:
Si se desea instalar el proyecto en un ambiente de desarrollo, se recomienda crear un entorno virtual ('make env' lo hace por usted :) )
y una vez creado installar las dependencias descritas en el archivo requirements.txt (make install).

La opción recomendad es instalar el proyecto con docker compose. En el archivo docker-compose.yaml se encuentran las instrucciones para realizarlo. Los unicos pasos que debe ejecutar son:


Construir la imagen del proyecto (docker build -t employes:1.0 .) con el comando:
```
$ make build
```

Y posteriomente:
```
$ docker-compose up
```
De esta manera tendra el servicio ejecutandose en el puerto 8000. La base de datos tambien está contenerizada, es una instancia de postgresql.

# TEST
Desafortunadamente los test solo se pueden ejecutar en un ambiente virutal (aun no se contenerizan). Se utiliza la herramienta 'nosetests'. Para esto es necesario ejecutar un contenedor con postgres
```
$ make db
```

y posteriormente

```
$ nosetests
```

Para que se pueda conecatar a la bd es necesario modificar un par de cosas en '/service/congid.py'.

Se debe cambiar el valor de "DATABASE_PASSWORD" a "postgresql" y el de "DATABASE_HOST" por "localhost", ya que al utilizar docker compose se crea una network unica para los contenedores.

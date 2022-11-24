# API Evaluacion KSP

## Description :book:
En este repositorio se encuentra la API REST, desarrollada con flask, para la evaluación tencnica de la empresa KSP.
El proyecto cuenta con un Make faile con comandos muy utiles.

## Installation :hammer:
Si se desea instalar el proyecto en un ambiente de desarrollo, se recomienda crear un entorno virtual ('make env' lo hace por usted :) )
y una vez creado installar las dependencias descritas en el archivo requirements.txt (make install).

La opción recomendad es instalar el proyecto con docker compose. En el archivo docker-compose.yaml se encuentran las instrucciones para realizarlo. Los unicos pasos que debe ejecutar son:
Construir la imagen del proyecto (docker build -t employes:10 .) con el comando:
```
$ make build
```


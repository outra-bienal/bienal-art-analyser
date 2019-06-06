Projeto para as análises de imagens para o projeto (OUTRA) 33ª Bienal de São Paulo

## Setup da aplicação

Esse é um projeto Django clásscio, então o processo é o tradicional:

```bash
# Clonar o repositório:
git clone git@github.com:outra-bienal/bienal-art-analyser.git

# Criar um virtualenv:
mkvirtualenv bienal-art-analyser -p /usr/bin/python3.6.5

# Criar containers e ativar o virtualenv
cd bienal-art-analyser
cp env.example .env  # você precisará editar o .env de acordo com suas configurações

# Instalar dependências
pip install -r dev-requirements.txt
```

## Setup da Infra

Certifique-se de que você tem o [Docker](https://www.docker.com/) instalado na sua máquina.
O projeto utiliza o Docker Compose para configurar as dependências de infraestrutura. Atualmente as depedências são o Postgres como banco de dados e o Redis para processamento assíncrono.

Para levantar os serviços basta executar:

```bash
cd bienal-art-analyser
docker-compose up -d
```

Além disso, há também a dependência com o [YOLO](https://pjreddie.com/darknet/yolo/) para conseguir executar o algorimo de detecção das imagens.
Siga [estes passos](https://pjreddie.com/darknet/install/) para instalar o Darknet e depois lembre-se de atualizar a variável de ambiente `DARKNET_DIR` dentro do seu `.env`.

Configure o vhost do rabbitmq com seus valores:

```bash
$ docker exec bienalartanalyser_art_analyser_rabbitmq_1 rabbitmqctl add_vhost bienal
$ docker exec bienalartanalyser_art_analyser_rabbitmq_1 rabbitmqctl add_user bienal bienal
$ docker exec bienalartanalyser_art_analyser_rabbitmq_1 rabbitmqctl set_user_tags bienal bienal
$ docker exec bienalartanalyser_art_analyser_rabbitmq_1 rabbitmqctl set_permissions -p bienal bienal ".*" ".*" ".*"
```

## Criar schema e popular base de dados
Com a infra de pé, execute o seguinte comando para criar e preparar o banco:

```bash
python project/manage.py migrate
```

## Executando a aplicação

Para acessar a aplicação, será necessário criar um usuário administrativo com o comando:

```bash
python project/manage.py createsuperuser
```

Depois disso, você pode rodar a apicação e acessá-la em [http://localhost:8000](http://localhost:8000) com o comando:

```bash
python project/manage.py runserver
```

## Rodando as análises e detecções
Como a parte de processamento das imagens é assíncrona, é necessário deixarmos rodando um worker do DjangoRQ para que ele consuma as mensagens que foram disparadas. Para isso, basta executar:

```bash
python project/manage.py rqworker
```


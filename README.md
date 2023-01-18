# Dramatiq dashboard using RabbitMQ

This project implements a dashboard for dramatiq when its running on RabbitMQ

## Install

To install all dependencies:

```
make install
```

To delete all dependencies:

```
make clean
```

## Run

To run the development server

```
make server
```

To run the production server

```
make prod
```
## Environment variables

| Env                | Type    | Description                                                  | Default value |
| ------------------ | ------- | ------------------------------------------------------------ | ------------- |
| RABBITMQ\_API\_URL | String  | The url that connects to the rabbitmq api                    | &nbsp;        |
| RABBITMQ\_USER     | String  | The rabbitmq username                                        | &nbsp;        |
| RABBITMQ\_PASS     | String  | The rabbitmq password                                        | &nbsp;        |
| RABBITMQ\_VHOST    | String  | The rabbitmq vhost                                           | &nbsp;        |
| RABBITMQ\_HOST     | String  | Hostname or IP Address to connect to for rabbitmq connection | localhost     |
| RABBITMQ\_PORT     | Integer | TCP port to connect to for rabbitmq connection               | 5672          |
| DEBUG              | Boolean | Debug setting                                                | &nbsp;        |

# OpenAPI documentation

To access openAPI documentation navigate to /openapi/ URL 
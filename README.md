## Dramatiq dashboard using RabbitMQ

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

To run the server

```
make server
```

## Environment variables

| Env          | Type    | Description                               | Default value |
| ------------ | ------- | ----------------------------------------- | ------------- |
| BASE\_URL    | String  | The url that connects to the rabbitmq api | &nbsp;        |
| RABBIT\_USER | String  | The rabbitmq username                     | &nbsp;        |
| RABBIT\_PASS | String  | The rabbitmq password                     | &nbsp;        |
| VHOST        | String  | The rabbitmq vhost                        | &nbsp;        |
| DEBUG        | Boolean | Debug setting                             | &nbsp;        |
| HOST         | String  | The host name                             | localhost     |
| PORT         | Integer | The port value                            | 5672          |
# OpenAPI documentation

To access openAPI documentation navigate to /openapi/ URL 
# Housing scrapper

This repository is based on https://github.com/rodrigouroz/housing_scrapper.

I didn't make a fork since I rewrote a big part of the code.

New features include:
  - asynchronous requests
  - type annotations
  - continuous integration setup

## Installation
This was tested with `Python 3.8`.

The recommended way to install dependencies is using a [virtual environment](https://docs.python.org/3/library/venv.html):

```bash
cd <PATH_TO_REPOSITORY>           # Change directory to this repository
python3 -m venv env               # Create a virtual environment folder
source env/bin/activate           # Activate virtual environment
pip3 install -r requirements.txt  # Install dependencies
```

## Configuration

There's a `configuration.example.yml` that you can use as a template. Copy that file and rename it to `configuration.yml`.

### Notifier

First you need to [create a Telegram Bot](https://core.telegram.org/bots) and configure the notifier with the following two parameters:

- The `token` is a string along the lines of `110201543:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw` that is required to authorize the bot and send requests to the Bot API. Keep your token secure and store it safely, it can be used by anyone to control your bot.

- The `chat_id` is a number that identifies the chat your bot will use to notify you. After talking to your bot first or adding it to a telegram group, you can visit https://api.telegram.org/botXXX:YYYYY/getUpdates to see the `chat_id`s (replace `XXX:YYYYY` with your authentication token).

### Providers

You can setup any of the providers as shown below:

```yaml
providers:
  zonaprop:
    base_url: 'https://www.zonaprop.com.ar'
    sources:
      - '/departamentos-alquiler-2-habitaciones.html'
      - '/ph-alquiler-2-habitaciones.html'
  argenprop:
    base_url: 'https://www.argenprop.com'
    sources:
      - '/departamento-alquiler-pais-argentina-2-dormitorios'
      - '/ph-alquiler-pais-argentina-2-dormitorios'
  mercadolibre:
    base_url: 'https://inmuebles.mercadolibre.com.ar'
    sources:
      - '/departamentos/alquiler/2-dormitorios/'
      - '/casas/alquiler/2-dormitorios/'
  properati:
    base_url: 'https://www.properati.com.ar'
    sources:
      - '/departamento/alquiler/ambientes:2'
  inmobusqueda:
    base_url: 'https://www.inmobusqueda.com.ar'
    sources:
      - '/departamento-alquiler-la-plata-casco-urbano.html?cambientes=2.'
```

## Running

You can put this in your crontab (uses the virtual environment mentioned in the [installation instructions](#Installation))
to run once every hour:

```bash
0 * * * * cd <PATH_TO_REPOSITORY> && env/bin/python3 -m main >> run.log 2>&1
```

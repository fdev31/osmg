# OSMG!

One platform many games

An platform aiming at radpid development of online slow-paced multiplayer games.

Check https://game.crava.ch/ for a quick demo

# Issues

Check [the ticket list](https://github.com/fdev31/osmg/blob/main/tickets.rst)

# Installing for development

You will need [just](https://github.com/casey/just), `npm` and `tox` at least.
To get started, just type:

```
just cleanenv
```

it will install every tool and create the base setup.

# Running

## Development

If you make changes to the content in the `locales` folder to change text, you'll need to type `just locales` to re-build the required files.

### Linting rules

for js (client):

```
just jslint
```

for python (server):

```
just pylint
```

### Running tests

```
just test
```

or for something more basic (no selenium)

```
just unit
```

### Re-build JS un debug mode (optional)

```
just dev
```

### Run the server

```
just run
```

### Use live compilation of the JS (optional)

```
just live
```

## Testing

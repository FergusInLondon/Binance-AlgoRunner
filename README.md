# ... @todo?

## Running

@todo

### Configuration

@todo

## Development

### Make Targets

The `Makefile` contains a selection of useful targets for simplfying the development workflow.

```
➜  Runner git:(v2/trader-actor) ✗ make help
help:            Show this help.
env-check:               Check that the current environment is capable of running AlgoRunner.
build:                   Build docker image, tagged "algorunner:<commit>"
lint:                    Run code quality checks
deps:                    Install all required dependencies (including for development)
test:                    Run all tests - including both unit tests and BDD feature tests
run:                     Run AlgoRunner
todo:                    Scan the codebase for items tagged with "@todo"

```

### Docker

There's also a `Dockerfile` contained in this repository; this builds a `python:3.9-slim` based Docker Image, with all development dependencies. This can be built using the aforementioned `Makefile`.

### Finding Tasks

The codebase is littered with `@todo` tags where low-hanging fruit is marked when discovered/encountered.

```
➜  adapters git:(huge-refactor) ✗ grep -r '@todo' .
    ./binance/test_user_transformations.py:    pass # @todo - transformation not implemented
➜  adapters git:(huge-refactor) ✗ ../..

➜  Runner git:(huge-refactor) ✗ grep -r '@todo' . | wc -l
      17
```

---

## August 2021 Update: AlgoRunner V2.0

A preview of this release is available in the [`develop`](https://github.com/FergusInLondon/Runner/tree/develop) branch; and progress tracking is available via the [Version 2 Project Board](https://github.com/FergusInLondon/Runner/projects/1).

This version aims to introduce a new design to allow easier exchange API interactions, concurrent processing of market orders, user definable algorithms *and* risk calculations, and improved dependency management.

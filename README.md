# ... @todo?

## Running

@todo

### Configuration

@todo

## Development

### Docker
There's also a `Dockerfile` contained in this repository; this installs all the requirements to commence development.

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

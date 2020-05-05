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

## Python Redux  
This is a port from the popular state management library [redux](http://redux.js.org/) but written entirely in Python.  All functionality (with the exception of the async testing done with redux-thunk and the Symbol Obversable stuff) have been converted into python.  This includes all relevant unit tests as well.  

NOTE: Only works with python 3.4.3 or greater

### Usage
Include the `python_redux` folder in your application (Not yet a `pip` package)  
```python
from python_redux import create_store, combine_reducers
from reducers import todos, filter

store = create_store(combine_reducers({
  'todos': todos,
  'filter': filter
}))

store['dispatch'](dict(type='ADD_TODO', text='Hello'))

print(store['get_state']().get('todos')) # ['Hello']
```

### Tests
Run `python tests.py`


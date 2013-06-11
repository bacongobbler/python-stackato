Python-Stackato
===============

Sample usage:
```python
from stackato import StackatoInterface

cfi = StackatoInterface("https://api.stackato-xxxx.local", "username", "password")
cfi.login()

cfi.delete_app('demo')
cfi.delte_service('demo')
```
or store token locally:
```python
from stackato import StackatoInterface

cfi = StackatoInterface("https://api.stackato-xxxx.local", "username", "password", store_token=True)
cfi.login()

cfi.delete_app('demo')
cfi.delte_service('demo')
```

More details to be added later.

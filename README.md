# **Web**  
A simple web framework for creating simple web applications with a built-in server intended for use at the development stage. __Web__ also supports [__uvicorn__](https://www.uvicorn.org/).  
### **Project structure:**  
```
MySite
├── run.py
├── app1
|   ├── __init__.py
|   ├── urls.py
|   └── views.py 
├── MySite
|   ├── __init__.py
|   ├── settings.py
└── └── asgi.py
```
The application must be launched from the root directory of the project.  
**Example**:  
```
...\MySite> python run.py
```  
```
...\MySite> uvicorn MySite.asgi:app
```

---

- `run.py`
```python
from web import Setup

if __name__ == '__main__':
    setup = Setup()
    setup.run()
```
---

- `MySite/__init__.py`
```python
from . import settings
```
---

- `MySite/settings.py`
```python  
from web.core.statics import sp

DEBUG = True # False
TRACING = True # False
STOP_ON_EXCEPTION = False  # works only with DEBUG=False

SERVER_HOST = '192.168.1.112'
SERVER_PORT = 80

INSTALL_APPS = [
    'main',
    'girls'
]

STATIC_FILE_DIRS = {
    'main': [
        sp('admin/', 'frontend/'),
        sp('admin/good', 'frontend/'),
    ]
}

ROOT_URLPATTERNS = [
    ('admin/', 'main'),
    ('girls/', 'girls')
]
```
---

- `MySite/asgi.py`
```python  
from web.core.asgi import asgi_app

app = asgi_app()
```
---


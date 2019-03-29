# mdatapipe package structure

`tree -d -I __pycache__ mdatapipe`

```
mdatapipe
|-- engines
|---engines/multiprocessing
|---base
├── client
├── core
│   ├── pipeline
│   └── plugin
└── plugins
    ├── collect
    │   └── using
    ├── filter
    │   └── using
    ├── parse
    │   └── using
    ├── transform
    │   ├── how
    │   └── using
    └── transport
        └── using
```

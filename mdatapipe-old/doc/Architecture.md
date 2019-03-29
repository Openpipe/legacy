# mdatapipe

A multiprocess plugin-driven engine for data collecting, analyzing and reporting.

## Pipeline description file

A pipeline description file is a YAML file containing a list of the plugins that wille be loaded. Plugins have an input/output queue, plugins read from their input queue, and inser objects into it's output queue «which is mappend to  next plugin input queue». Each plugin will run on it's own

## Plugins

There are several categories and sub-categories of plugins.

## Collectors

The collector plugins are divided into two subcategories: _when_ and _what_.

### Collectors - When

A _when_ plugin does not watch it's input queue, instead it watchs resources and produces timestamp when a specific condition is met. For example, the `on_interval: 10m` will generate produce timestamps every 10 minutes.

NOTE: Every pipeline must start whith a _when_ plugin.

### Collectors - What

A _what_ plugin receives timestamps on it's input queue, they will then acquire "raw" data from a configured resource, and submit that data to the next plugin. An example of a _what_ plugin is the `on_file_delta_lines: filename` which will acquire all the new lines found on file since the last collection was run.

## Parser

A _parser_ plugin receives raw data «e.g. a list of lines», parses it, and produces a list of JSON objects.

## Transform

A _transform_ plugin receives a list of JSON objects, applies a set of transformation rules, and produces an list of JSON objects with the transformed data.

## Aggregator

An _aggregation plugin receives a list of JSON objects, produces aggregation results based on aggregration rules.

Example:


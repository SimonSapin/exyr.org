title: "cairocffi: CFFI-based Python bindings for cairo"
published: 2014-09-19
summary: |
    What is [cairocffi](https://pythonhosted.org/cairocffi/),
    how does it relate to pycairo,
    and why did I build it?

*Note:* cairocffi is kinda old news, but I was asked recently about it.
This is the anwser, [made public](http://blog.codinghorror.com/when-in-doubt-make-it-public/).

[Cairo](http://cairographics.org/) is a 2D vector graphics library
with support for multiple backends including
image buffers, PNG, PostScript, PDF, and SVG file output.

[pycairo](http://cairographics.org/pycairo/) is a set of Python bindings for cairo
that has been around for a long time.
Unfortunately, it also seems abandonned.
I’ve sent [a couple](https://bugs.freedesktop.org/show_bug.cgi?id=58771)
of [patches](https://bugs.freedesktop.org/show_bug.cgi?id=58772)
more than a year ago and haven’t heard since.

I’ve considered taking over maintainership of pycairo or forking it
but to be honest, working on it is kind of a pain.
pycairo is a CPython [extension](https://docs.python.org/extending/extending.html) written in C,
which means it has to manually increment and decrement reference counts of Python objects.
Failure to do so correctly means leaking memory or crashing with a segmentation fault.
Even with reference counting aside,
every little thing is tedious when interacting with CPython from C code.

Now, the only reason pycairo is written in C
is to be able to call functions from cairo, a C library.
Enter [CFFI](http://cffi.readthedocs.org/),
a Python library for calling C functions from Python code.

Writing a new set of bindings using CFFI seemed way easier[^1]
than maintining pycairo and fixing a bunch of its issues.
Thus, [cairocffi](http://pythonhosted.org/cairocffi/) was born.
It implements the same Python API as pycairo
and so is a “drop-in” replacement.
For example, [CairoSVG](http://cairosvg.org/) can use either one,
without code change other than [`import` statements](
https://github.com/Kozea/CairoSVG/blob/fcc0857cc3d35b27e7ac00ede4cc50a56e4edf49/cairosvg/surface/__init__.py#L24-L30).

CFFI’s `dlopen()` method allows loading shared libraries dynamically.
Users can therefore get a pre-compiled cairo from somewhere and use cairocffi from source,
without a working C compiler being required (which is a pain on Windows).
And I don’t need to maintain binaries for various plateforms either.

From the users’ point of view:

* cairocffi uses standard Python packaging tools, and thus can easily be installed in a virtualenv. Doing so with pycairo requires [some tricks](http://stackoverflow.com/a/11686044/1162888).
* The same code base runs on Python 2.x and 3.x (whereas py2cairo is separate from pycairo).
* It runs on PyPy (and anywhere CFFI does).
* It has bindings for some cairo features that were added after the last pycairo release.
  Just [tell me](https://github.com/SimonSapin/cairocffi/issues/20) if you need more.

pycairo is dead, long live [cairocffi](http://pythonhosted.org/cairocffi/)!


[^1]:
    Compare cairocffi’s [`context.py`](https://github.com/SimonSapin/cairocffi/blob/f5e1f2cf27f3cebfdecb60c9c32c12dd35de141c/cairocffi/context.py#L432-L471):

        #!python
        def set_dash(self, dashes, offset=0):
            """
            ... (32 lines of docstring)
            """
            cairo.cairo_set_dash(
                self._pointer, ffi.new('double[]', dashes), len(dashes), offset)
            self._check_status()

    … to pycairo’s [`context.c`](http://cgit.freedesktop.org/pycairo/tree/src/context.c?id=75e82a1b3f495a3abbc78e50a5c66356d320fb15#n826):

        #!c
        static PyObject *
        pycairo_set_dash (PycairoContext *o, PyObject *args) {
          double *dashes, offset = 0;
          int num_dashes, i;
          PyObject *py_dashes;

          if (!PyArg_ParseTuple (args, "O|d:Context.set_dash", &py_dashes, &offset))
            return NULL;

          py_dashes = PySequence_Fast (py_dashes,
                                       "first argument must be a sequence");
          if (py_dashes == NULL)
            return NULL;

          num_dashes = PySequence_Fast_GET_SIZE(py_dashes);
          dashes = PyMem_Malloc (num_dashes * sizeof(double));
          if (dashes == NULL) {
            Py_DECREF(py_dashes);
            return PyErr_NoMemory();
          }

          for (i = 0; i < num_dashes; i++) {
            dashes[i] = PyFloat_AsDouble(PySequence_Fast_GET_ITEM(py_dashes, i));
            if (PyErr_Occurred()) {
              PyMem_Free (dashes);
              Py_DECREF(py_dashes);
              return NULL;
            }
          }
          cairo_set_dash (o->ctx, dashes, num_dashes, offset);
          PyMem_Free (dashes);
          Py_DECREF(py_dashes);
          RETURN_NULL_IF_CAIRO_CONTEXT_ERROR(o->ctx);
          Py_RETURN_NONE;
        }

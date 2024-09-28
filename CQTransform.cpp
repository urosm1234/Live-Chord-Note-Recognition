#define PY_SSIZE_T_CLEAN


#include <Python.h>
#include <numpy/arrayobject.h>

static PyObject* HPCP(PyObject* self, PyObject* args){
    PyObject* input_obj = NULL;
    int bins;
    int M;

    if (!PyArg_ParseTuple(args, "Oii", &input_obj, &bins, &M)) {
        return NULL;
    } 
    PyArrayObject* cqt = (PyArrayObject*) PyArray_FROM_OF(input_obj, NPY_DOUBLE);
    if (cqt == NULL) {
        PyErr_SetString(PyExc_TypeError, "Input should be a NumPy array of floats (double).");
        return NULL;
    }
    npy_intp* dims = PyArray_DIMS(cqt);
    npy_intp dimsout[1] = {bins};
    double** input_data;// = (double*)PyArray_DATA(cqt);
    PyArray_AsCArray((PyObject **) &cqt, &input_data, dims, 2, PyArray_DescrFromType(NPY_DOUBLE));

     // Create a new NumPy array for the result
     //(84, 33)
    PyArrayObject* result_array = (PyArrayObject*) PyArray_SimpleNew(1, dimsout, NPY_DOUBLE);
    if (result_array == NULL) {
        Py_DECREF(cqt);
        return NULL;
    }
    double* result_data = (double*) PyArray_DATA(result_array);
    double sum = 0;
    for(int i=0; i < bins; i++)
    {
        for(int j = 0;j<M;j++)
        {
            for(int p = 0;p<dims[1]; p++)
                sum+=input_data[i+j*bins][p];
        }
        result_data[i] = sum;
        sum = 0;
    }

    Py_DECREF(cqt);
    return (PyObject*) result_array;
}

/*def PCP(cqt, bins, M):
    CH = np.zeros(bins)
    for b in range(bins):
        CH[b] = np.sum(cqt[b + (np.arange(M) * bins)])
    return CH*/

static PyMethodDef MyMethods[] = {
    {"HPCP", HPCP, METH_VARARGS, "Preforms HCP"},
    {NULL, NULL, 0, NULL}  // Sentinel
};

static struct PyModuleDef CQTransform = {
    PyModuleDef_HEAD_INIT,
    "CQTransform",  // Module name
    NULL,        // Module documentation
    -1,          // Keep state in global variables
    MyMethods    // Methods
};


PyMODINIT_FUNC PyInit_CQTransform(void) {
    import_array();  // Initialize the NumPy API
    return PyModule_Create(&CQTransform);
}
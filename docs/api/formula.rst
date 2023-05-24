Boolean formula manipulation (:mod:`pysat.formula`)
===================================================

.. code-block:: python

    >>> from pysat.formula import Var as v, Const as c
    >>> from pysat.solvers import Minisat22
    >>> m = Minisat22()
    >>> x, y, z = v('x'), v('y'), v('z')
    >>> f = (x > y) & (y > z) & (z > c(False))
    >>> m.append_formula(f.to_CNF().clauses)
    >>> m.solve()
    True
    >>> def val(var):
    ...     return m.get_model()[var.content-1] > 0
    >>> val(x), val(y), val(y)
    (False, False, False)

.. toctree::
    :maxdepth: 3

    formula_utils
    formula_base
    formula_normal

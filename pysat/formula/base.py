#!/usr/bin/env python
#-*- coding:utf-8 -*-
##
## formula.py
##
##  Created on: Dec 7, 2016
##      Author: Alexey S. Ignatiev
##      E-mail: aignatiev@ciencias.ulisboa.pt
##

"""
    ===============
    List of classes
    ===============

    .. autosummary::
        :nosignatures:

        Const
        Var
        Not
        And
        Or
        Implies
        Equals
        NotEquals

    ==================
    Module description
    ==================

    placeholder

    ==============
    Module details
    ==============
"""

#
#==============================================================================
from __future__ import print_function
import abc
from .utils import *
from .normal import *

#
#==============================================================================
class FormulaException(Exception):
    pass

default_pool = IDPool()
default_true = default_pool.id('true')

class Formula(abc.ABC):
    """
        Parent class of all boolean formulas.

        The syntax rules of boolean formulas are as follows:

        - :class:`Var` and :class:`Const` are formulas.
        - if `a` is a formula, then `~a` is a formula.
        - if `a`, `b` are formulas, then `a & b`, `a | b`, and `a > b` are formulas.

        Example:

        .. code-block:: python

            >>> from pysat.formula import Var as v, Const as c
            >>> v(1) & ~v(2) > c(False)
            Implies(And(Var(1),Not(Var(2))),Const(False))
    """
    @abc.abstractmethod
    def __init__():
        pass

    def __invert__(self):
        """
            Negation. The operator '~'.
        """
        return Not(self)

    def __and__(self, other):
        """
            Conjunction. The operator '&'.
        """
        if type(self) is And and type(other) is And:
            return And(*self.children, *other.children)
        elif type(self) is And:
            return And(*self.children, other)
        else:
            return And(self, other)

    def __iand__(self, other):
        """
            In-place conjunction. The operator '&='.
        """
        if type(self) is And and type(other) is And:
            self.children.extend(other.children)
        elif type(self) is And and issubclass(type(other), Formula):
            self.children.append(other)
        else:
            raise FormulaException
        return self

    def __or__(self, other):
        """
            Disjunction. The operator '|'.
        """
        if type(self) is Or and type(other) is Or:
            return Or(*self.children, *other.children)
        elif type(self) is Or:
            return Or(*self.children, other)
        else:
            return Or(self, other)

    def __ior__(self, other):
        """
            In-place disjunction. The operator '|='.
        """
        if type(self) is Or and type(other) is Or:
            self.children.extend(other.children)
        elif type(self) is Or and issubclass(type(other), Formula):
            self.children.append(other)
        else:
            raise FormulaException
        return self

    def __gt__(self, other):
        """
            Implication. The operator '>'.
        """
        return Implies(self, other)

    def __eq__(self, other):
        """
            Equality. The operator '=='.
        """
        return Equals(self, other)

    def __ne__(self, other):
        """
            Inequality. The operator '!='.
        """
        return NotEquals(self, other)

    def to_CNF(self):
        v, c = self.tseitin()
        cnf = CNF(from_clauses=c)
        cnf.append([v])
        return cnf

class AtomicFormula(Formula, abc.ABC):
    """
        Parent class of all atomic boolean formulas. Atomic formulas,
        or prime formulas, are zeroary formulas consisting
        of only propositional variables or truth constants [2]_; that is,
        :math:`x_{1},x_{2},x_{3},\\ldots` and :math:`\\top` and :math:`\\bot`
        are atomic fomulas.

        .. [2] W. Rautenberg. *A concise introduction to mathematical logic*, 3rd edition. Universitext, Springer New York, 2010.
    """
    @abc.abstractmethod
    def __init__():
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.content)})"

class CompositeFormula(Formula, abc.ABC):
    """
        Parent class of all non-atomic boolean formulas.
        Non-atomic formulas involve connective symbols:
        :math:`\\neg`, :math:`\\wedge`, etc.
    """
    @abc.abstractmethod
    def symbol():
        pass

class UnaryFormula(CompositeFormula, abc.ABC):
    """
        Parent class of all unary boolean formulas.
        Unary formulas are made up of logical symbols of arity :math:`1` [2]_.
        For example, the negation symbol :math:`\\neg`;
        if :math:`\\phi` is a formula, then all the formulas
        of the form :math:`\\neg\\phi` are unary formulas.
    """
    def __init__(self, input, pool=default_pool):
        assert issubclass(type(input), Formula)
        assert type(pool) is IDPool

        self.pool = pool
        self.child = input

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.child)})"

    def __str__(self):
        if issubclass(type(self.child), AtomicFormula):
            return f"{self.symbol()}{self.child}"
        else:
            return f"{self.symbol()}({self.child})"

class MultaryFormula(CompositeFormula, abc.ABC):
    """
        Parent class of all multary boolean formulas.
        Multary formulas are made up of logical symbols of arity :math:`n \\geq 0`.
        For example, the multary conjunction and disjunction symbols,
        :math:`\\bigwedge` and :math:`\\bigvee`;
        if :math:`\\phi_{i},\\psi_{i}` for all
        :math:`i=1,2,\\ldots,n` are formulas, then all the formulas
        of the form :math:`\\bigwedge_{i=1,2,\\ldots,n} \\phi_{i}`
        and :math:`\\bigvee_{i=1,2,\\ldots,n} \\psi_{i}` are :math:`n`-ary formulas.
    """
    def __init__(self, *inputs, pool=default_pool):
        assert all(issubclass(type(input), Formula) for input in inputs)
        assert type(pool) is IDPool

        self.pool = pool
        self.children = list(inputs)

    def __repr__(self):
        return f"{self.__class__.__name__}({','.join(repr(child) for child in self.children)})"

    def __str__(self):
        return f" {self.symbol()} ".join(map(str, self.children))

class BinaryFormula(MultaryFormula, abc.ABC):
    """
        Parent class of all binary boolean formulas.
        Binary formulas are a specialization of multary formulas
        where they are made up of logical symbols of arity :math:`n = 2` [2]_.
        For example, the binary conjunction and disjunction symbols,
        :math:`\\wedge` and :math:`\\vee`;
        if :math:`\\phi,\\psi` are formulas, then all the formulas
        of the form :math:`\\phi \\wedge \\psi`
        and :math:`\\phi \\vee \\psi` are binary formulas.
    """
    def __init__(self, lhs_input, rhs_input, pool=default_pool):
        assert issubclass(type(lhs_input), Formula) and issubclass(type(rhs_input), Formula)
        assert type(pool) is IDPool

        self.pool = pool
        self.children = [lhs_input, rhs_input]

class Const(AtomicFormula):
    """
        Logical constants. There are only two logical constants,
        verum and falsum [2]_, or truth and falsity,
        or tautology and contradiction, or :math:`1` and :math:`0`
        , denoted as :math:`\\top` and :math:`\\bot`.

        Example:

        .. code-block:: python

            >>> from pysat.formula import Var as v, Const as c
            >>> c(True)
            Const(True)
            >>> c(False)
            Const(False)
    """
    def __init__(self, content, pool=default_pool, id=default_true):
        assert type(content) is bool
        assert type(pool) is IDPool and type(id) is int

        self.pool = pool
        self.content = content
        self.id = id if content else -id

    def __str__(self):
        return f"{self.content}"

    def tseitin(self):
        return self.id, []

class Var(AtomicFormula):
    """
        Propositional variables. They are numbered by :math:`\mathbb{N}`,
        denoted as :math:`x_{1},x_{2},x_{3},\\ldots`.

        Example:

        .. code-block:: python

            >>> from pysat.formula import Var as v, Const as c
            >>> v(1)
            Var(1)
    """
    def __init__(self, content, pool=default_pool):
        assert type(content) is int or type(content) is str
        assert type(pool) is IDPool

        self.pool = pool
        self.content_is_str = False
        if type(content) is int:
            self.content = content
        else:
            self.content_is_str = True
            self.content = self.pool.id(content)
        while self.content > self.pool.top:
            self.pool.id()

    def __str__(self):
        if self.content == self.pool.id('true'):
            if self.content > 0:
                return f"True"
            elif self.content < 0:
                return f"False"
            else:
                raise FormulaException
        if self.content_is_str:
            return f"x_{self.pool.obj(self.content)}"
        else:
            return f"x{self.content}"

    def tseitin(self):
        return self.content, []

class Not(UnaryFormula):
    """
        Logical negation. A unary symbol, denoted as :math:`\\neg`.

        It can be constructed with the operator `~`.

        Example:

        .. code-block:: python

            >>> from pysat.formula import Var as v, Const as c
            >>> ~v(1)
            Not(Var(1))
    """
    @staticmethod
    def symbol():
        return '~'

    def tseitin(self):
        fresh = self.pool.id()
        sub, clauses = self.child.tseitin()
        clauses.append([fresh, sub])   # fresh < ~sub
        clauses.append([-fresh, -sub]) # fresh > ~sub
        return fresh, clauses

class And(MultaryFormula):
    """
        Logical conjunction. An :math:`n`-ary symbol,
        , denoted as :math:`\\bigwedge`; in particular,
        it is :math:`\\top` when :math:`n = 0` and the unary identity
        when :math:`n = 1`.

        It can be constructed with the operator `&`.

        Example:

        .. code-block:: python

            >>> from pysat.formula import Var as v, Const as c
            >>> v(1) & v(2) & v(3)
            And(Var(1),Var(2),Var(3))

        There is also an in-place operator `&=`.

        Example:

        .. code-block:: python

            >>> from pysat.formula import Var as v, Const as c
            >>> p = v(1) & v(2)
            >>> p &= v(3)
            >>> p
            And(Var(1),Var(2),Var(3))
    """
    @staticmethod
    def symbol():
        return '&'

    def tseitin(self):
        fresh = self.pool.id()
        c = [fresh] # fresh < (sub & sub & ...)
        clauses = []
        for child in self.children:
            sub, cs = child.tseitin()
            clauses += cs
            clauses.append([-fresh, sub]) # fresh > (sub & sub & ...)
            c.append(-sub)
        clauses.append(c)
        return fresh, clauses

class Or(MultaryFormula):
    """
        Logical disjunction. An :math:`n`-ary symbol
        , denoted as :math:`\\bigvee`; in particular,
        it is :math:`\\bot` when :math:`n = 0` and the unary identity
        when :math:`n = 1`.

        It can be constructed with the operator `|`.

        Example:

        .. code-block:: python

            >>> from pysat.formula import Var as v, Const as c
            >>> v(1) | v(2) | v(3)
            Or(Var(1),Var(2),Var(3))

        There is also an in-place operator `|=`.

        Example:

        .. code-block:: python

            >>> from pysat.formula import Var as v, Const as c
            >>> p = v(1) | v(2)
            >>> p |= v(3)
            >>> p
            Or(Var(1),Var(2),Var(3))
    """
    @staticmethod
    def symbol():
        return '|'

    def tseitin(self):
        fresh = self.pool.id()
        c = [-fresh] # fresh > (sub | sub | ...)
        clauses = []
        for child in self.children:
            sub, cs = child.tseitin()
            clauses += cs
            clauses.append([fresh, -sub]) # fresh < (sub | sub | ...)
            c.append(sub)
        clauses.append(c)
        return fresh, clauses

class Implies(BinaryFormula):
    """
        Logical implication. A binary symbol, denoted as :math:`\\implies`.

        It can be constructed with the operator `>`.

        Example:

        .. code-block:: python

            >>> from pysat.formula import Var as v, Const as c
            >>> v(1) > v(2)
            Implies(Var(1),Var(2))
    """
    @staticmethod
    def symbol():
        return '>'

    def tseitin(self):
        fresh = self.pool.id()
        clauses = []
        sub_lhs, cs_lhs = self.children[0].tseitin()
        sub_rhs, cs_rhs = self.children[1].tseitin()
        clauses += cs_lhs
        clauses += cs_rhs
        clauses.append([fresh, sub_lhs])  # fresh < (sub_lhs > sub_rhs)
        clauses.append([fresh, -sub_rhs]) # fresh < (sub_lhs > sub_rhs)
        clauses.append([-fresh, -sub_lhs, sub_rhs]) # fresh > (sub_lhs > sub_rhs)
        return fresh, clauses

class Equals(BinaryFormula):
    """
        Logical biconditional. A binary symbol, denoted as :math:`\\Longleftrightarrow`.

        It can be constructed with the operator `==`.

        Example:

        .. code-block:: python

            >>> from pysat.formula import Var as v, Const as c
            >>> v(1) == v(2)
            Equals(Var(1),Var(2))
    """
    @staticmethod
    def symbol():
        return '=='

    def tseitin(self):
        fresh = self.pool.id()
        clauses = []
        sub_lhs, cs_lhs = self.children[0].tseitin()
        sub_rhs, cs_rhs = self.children[1].tseitin()
        clauses += cs_lhs
        clauses += cs_rhs
        clauses.append([fresh, -sub_lhs, -sub_rhs]) # fresh < (sub_lhs == sub_rhs)
        clauses.append([fresh, sub_lhs, sub_rhs])   # fresh < (sub_lhs == sub_rhs)
        clauses.append([-fresh, -sub_lhs, sub_rhs]) # fresh > (sub_lhs == sub_rhs)
        clauses.append([-fresh, sub_lhs, -sub_rhs]) # fresh > (sub_lhs == sub_rhs)
        return fresh, clauses

class NotEquals(BinaryFormula):
    """
        Logical exclusive disjunction. A binary symbol, denoted as :math:`\\oplus`.

        It can be constructed with the operator `!=`.

        Example:

        .. code-block:: python

            >>> from pysat.formula import Var as v, Const as c
            >>> v(1) != v(2)
            NotEquals(Var(1),Var(2))
    """
    @staticmethod
    def symbol():
        return '!='

    def tseitin(self):
        fresh = self.pool.id()
        clauses = []
        sub_lhs, cs_lhs = self.children[0].tseitin()
        sub_rhs, cs_rhs = self.children[1].tseitin()
        clauses += cs_lhs
        clauses += cs_rhs
        clauses.append([fresh, -sub_lhs, sub_rhs]) # fresh < (sub_lhs != sub_rhs)
        clauses.append([fresh, sub_lhs, -sub_rhs]) # fresh < (sub_lhs != sub_rhs)
        clauses.append([-fresh, -sub_lhs, -sub_rhs]) # fresh > (sub_lhs != sub_rhs)
        clauses.append([-fresh, sub_lhs, sub_rhs])   # fresh > (sub_lhs != sub_rhs)
        return fresh, clauses

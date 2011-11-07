title: "Multicorn: Access foreign data in PostgreSQL with Python"
public: true
published: 2011-11-07
tags: [kozea]
summary:
    We just released [Multicorn](http://multicorn.org/). It enables you
    to write Foreign Data Wrappers for PostgreSQL in Python. Any data
    source can be exposed as a table and queried with full SQL.

We just released [Multicorn](http://multicorn.org/). It enables you
to write Foreign Data Wrappers for PostgreSQL in Python. Any data
source can be exposed as a table and queried with full SQL. A simple wrapper
can be as short as [a dozen lines of code](
https://github.com/Kozea/Multicorn/blob/master/python/multicorn/processfdw.py).

With this you can have data from various authoritative sources (like people
in a LDAP directory) and access it in a single place with any ORM or other
tool you’re used to.

The website for the new and shiny Multicorn is
[multicorn.org](http://multicorn.org/).

You can stop reading here. Everything else is anecdotal history.

How we got here: Dyko and Kalamar
=================================

We at Kozea have been trying to do this for a long time, but our initial
approach was much higher on the stack. [Dyko](http://dyko.org/) was our
homegrown do-it-all über-framework. Kraken was Dyko’s web framework part,
but then [Flask](http://flask.pocoo.org/) was released, we switch to it
and the world got much saner.

However the bigger part of Dyko was Kalamar, a unified data access library.
All you data are belong to Kalamar. SQL databases, LDAP directories,
files in a filesystem, meta-data in these files, entries in RSS feeds,
you name it. All you had to do to add a new kind of data source was write
an *access point* in Python. Sounds familiar?

The problem with Kalamar is that everything is at the application level.
This means that we had to reinvent ways to make queries to our (heterogeneous)
data stores and to represent the results. Of course what we came up with
was far from being as good as existing tools such as SQLAlchemy.
SQLAlchemy was actually used for SQL databases, but hidden behind the Kalamar
API as it did not support non-SQL data sources.

Though Kalamar went through multiple re-design and complete rewrites,
the ability to do any join came somewhat late and was kind of special cased.

Multicorn, First of the name
============================

It was time for another rewrite, but this time our ambitions were much higher.
Enough for the project to earn a new name and logo: Multicorn. However
this was still not today’s Multicorn.

The first Multicorn defined a set of basic operations like map, filter and
reduce that could be chained and combined arbitrarily. Each of these could
take sub-expressions as arguments. Any kind of join or group by could be
expressed that way.

Every operation was first implemented in Python. The user API was great and
it worked, but of course it was slow if you started having a lot of data.
Then it was the responsibility of each access point to add “optimizations”
by implementing the operations it could (eg. by translating it to SQL) to
defer more work to the backend and do less in Python.

The first Multicorn was really LINQ for Python. Except it didn’t work.
The implementation soon grew too complicated to be manageable. At some point
we almost had a new language with static analysis and type inference.

One fine week of September, all other projects were put on hold until we
had a working and usable by the end of the week. This is when magic
happend. On Monday morning, our crazy DBA announced the release of
PostgreSQL 9.1. Among other cool things, this new version had **Foreign
Data Wrappers**. We knew then that Multicorn was gonna be something else
entirely…

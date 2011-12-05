title: Hashing passwords the Right Way
public: true
published: 2011-12-05
tags: [passwords, web-development, snippets]
summary:
    Don’t store passwords in plain text. Don’t use a fast algorithm.
    And don’t forget the salt.

**Short answer**: I chose PBKDF2, but bcrypt and scrypt are good too.
In any case, use a constant-time comparison to avoid timing attacks.
Find the code below.

---

So you’re writing some application where users log in with passwords.
As you already know (or so I hope!), you [should not store passwords in plain text](
http://tea.moertel.com/articles/2006/12/15/never-store-passwords-in-a-database).
There is plenty already on the *why*, so I’ll focus on the *how*.

The scenario we want to protect from is an attacker getting access to the
database. Of course you should try to prevent that in the first place,
but it has happened before.
Traditional, reversible cryptography does not help: if the database was stolen,
the key may have been stolen too. Thus, we need a one-way hash.

SHA-256 is not known to be broken at the time of this writing, while
[MD5](http://www.schneier.com/blog/archives/2005/06/more_md5_collis.html) and
[SHA-1](http://www.schneier.com/blog/archives/2005/02/sha1_broken.html) are.

The basic idea is to store `hash = sha256(password)` instead of the password
itself. However this method vulnerable to Rainbow Table attacks where a hash
is compared against a big table of pre-computed hashes. Creating such a table
is expensive (takes time), but after that it can be used for all entries in the
database. A salt protects against this:
`hash = salt + sha256(salt + password)`. Salts should be 8 bytes or longer,
unique and random.

Salting is good but it [does not protect](
http://codahale.com/how-to-safely-store-a-password/)
against dictionary and brute force attacks. This is because SHA-256 and similar
hashing functions are designed to be fast.

To make it slower we could just apply SHA-256 to its own result many times.
This number of application is the *work factor*. When computers become faster
next year we can increase the work factor to keep up with Moore’s law.
However, the first rule of designing a crypto-system is: Don’t.

[PBKDF2](http://en.wikipedia.org/wiki/PBKDF2),
[bcrypt](http://www.usenix.org/events/usenix99/provos/provos_html/index.html)
and [scrypt](http://www.tarsnap.com/scrypt.html)
are all reputable hashing functions with a work factor. See [this answer](
http://security.stackexchange.com/questions/4781/do-any-security-experts-recommend-bcrypt-for-password-storage/6415#6415)
to compare them. I chose PBKDF2 since it is easiest to implement in Python
and I judged it good enough based on what I read about it.
There are several implementations of PBKDF2 for Python out there. I picked
[Armin Ronacher’s](https://github.com/mitsuhiko/python-pbkdf2) for its
simplicity (15 lines of actual code).

One more thing where we need to be careful is [timing attacks](
http://carlos.bueno.org/2011/10/timing.html). If we use the `==` operator
to check a hash, it will compare byte-by-byte and return on the first
inequality. This timing leaks information to the attacker who could
guess the correct hash without even getting access to the database.
This attack is [more plausible](http://codahale.com/a-lesson-in-timing-attacks/)
than one might first think. But even if it is not, a constant-time comparison
is easy (See the the code below.) so there is no reason not to do it.

To wrap up: PBKDF2 with random, unique salts and constant-time comparison.

Finally, it is useful to store the algorithm parameters such as the work
factor next to the hash and its salt. That way, if we later want to change
these parameters we don’t need to throw away old hashes and reset everyone’s
password. Old hashes can stay valid and be re-created on next log in.

We need some code to tie all this together and it’s pretty generic.
The whole point of this article is actually to provide it.
This is the code I use in production:

    :::python
    import hashlib
    from os import urandom
    from base64 import b64encode, b64decode
    from itertools import izip

    # From https://github.com/mitsuhiko/python-pbkdf2
    from pbkdf2 import pbkdf2_bin


    # Parameters to PBKDF2. Only affect new passwords.
    SALT_LENGTH = 12
    KEY_LENGTH = 24
    HASH_FUNCTION = 'sha256'  # Must be in hashlib.
    # Linear to the hashing time. Adjust to be high but take a reasonable
    # amount of time on your server. Measure with:
    # python -m timeit -s 'import passwords as p' 'p.make_hash("something")'
    COST_FACTOR = 10000


    def make_hash(password):
        """Generate a random salt and return a new hash for the password."""
        if isinstance(password, unicode):
            password = password.encode('utf-8')
        salt = b64encode(urandom(SALT_LENGTH))
        return 'PBKDF2${}${}${}${}'.format(
            HASH_FUNCTION,
            COST_FACTOR,
            salt,
            b64encode(pbkdf2_bin(password, salt, COST_FACTOR, KEY_LENGTH,
                                 getattr(hashlib, HASH_FUNCTION))))


    def check_hash(password, hash_):
        """Check a password against an existing hash."""
        if isinstance(password, unicode):
            password = password.encode('utf-8')
        algorithm, hash_function, cost_factor, salt, hash_a = hash_.split('$')
        assert algorithm == 'PBKDF2'
        hash_a = b64decode(hash_a)
        hash_b = pbkdf2_bin(password, salt, int(cost_factor), len(hash_a),
                            getattr(hashlib, hash_function))
        assert len(hash_a) == len(hash_b)  # we requested this from pbkdf2_bin()
        # Same as "return hash_a == hash_b" but takes a constant time.
        # See http://carlos.bueno.org/2011/10/timing.html
        diff = 0
        for char_a, char_b in izip(hash_a, hash_b):
            diff |= ord(char_a) ^ ord(char_b)
        return diff == 0

As usual, the code is BSD licensed (as is Armin’s PBKDF2 implementation) and
available [by itself](
https://github.com/SimonSapin/snippets/blob/master/hashing_passwords.py).

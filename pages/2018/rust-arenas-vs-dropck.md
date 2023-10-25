title: "Borrow cycles in Rust: arenas v.s. drop-checking"
published: 2018-02-17
summary: |
    Creating cycles with `&T` borrowed references in rust is tricky, but possible.
    Drop-checking seems to prevent optimizing practical uses,
    but there’s an escape hatch (that’s only available on Nightly for now),
    as well as a hack (that works on Rust Stable).

[Ownership](https://doc.rust-lang.org/book/second-edition/ch04-01-what-is-ownership.html)
and [borrowing](https://doc.rust-lang.org/book/second-edition/ch04-02-references-and-borrowing.html)
are the fundamentals of data structures in Rust.

However, both taking owneship of a value (moving it) or taking a reference to it
can only happen *after* the value was created.
This ordering seems to prevent having any cycle in a data structure,
even though that’s sometimes useful or necessary.
For example in a web page’s content tree, from any DOM node,
one can easily access (if any) its first and last child, previous and next sibling,
(so children of a node form a doubly-linked list) and parent.
Some other applications might need to manipulate arbitrary graphs in their full generality.

There a [few different approaches](https://github.com/SimonSapin/rust-forest)
to work around this apparent limitation:

* Reference-counting with `Rc` or `Arc`,
* Integer indices / identifiers into shared storage,
* `&T` borrows / references with an arena allocator.

This post focuses on the latter, since references are most ergonomic in my opinion.

Let’s build it step-by-step.
We’ll use `u32` integers as placeholders for a node’s payload,
arbitrary useful data associated to it.

# Building `&T` reference cycles

Before the compiler will even consider values that (indirectly) reference themselves,
we’ll need types that reference themselves.
A first naïve attempt produces a type that would take infinite space to spell out,
and the compiler doesn’t like that.

```rust,compile_fail
let mut a = (42_u32, None);
let b = (7_u32, Some(&a));
// error[E0308]: mismatched types
a.1 = Some(b);
//    ^^^^^^^ cyclic type of infinite size
```

We’ll need to make a type with a name so that its definition can be recursive.

```rust,compile_fail
struct Node<'a> {
    value: u32,
    next: Option<&'a Node<'a>>,
}
let mut a = Node { value: 42, next: None };
// error[E0506]: cannot assign to `a.next` because it is borrowed
let b = Node { value: 7, next: Some(&a) };
//                                   - borrow of `a.next` occurs here
a.next = Some(&b);
// ^^^^^^^^^^^^^^ assignment to borrowed `a.next` occurs here
```

… aaand, today’s first borrow-checking error!

Assigning with `=` is similar to taking a `&mut T` reference:
it requires exclusive access.
(By the way `&mut T` and `&T` should be called exclusive and shared references,
rather than mutable and immutable, since that’s what they’re really about.)

To be able to mutate part of a node while it is already borrow,
well use `Cell`’s
[interior mutability](https://doc.rust-lang.org/book/second-edition/ch15-05-interior-mutability.html).

```rust,compile_fail
use std::cell::Cell;

struct Node<'a> {
    value: u32,
    next: Cell<Option<&'a Node<'a>>>,
}

let a = Node { value: 42, next: Cell::new(None) };
let b = Node { value: 7, next: Cell::new(Some(&a)) };
// error[E0597]: `b` does not live long enough
a.next.set(Some(&b));
//               ^ borrowed value does not live long enough
// `b` dropped here while still borrowed
```

Now we get to the heart of the issue: neither `a` or `b` is allowed to *outlive* the other.
The only way a cycle can be legal is if they have *the same lifetime*.

The way we had to write `&'a Node<'a>`, repeating the same `'a` lifetime,
was already hinting at this.
The lifetime of the outer reference is the same as the one inside the referenced node.
If we tried to make them different like `&'a Node<'b>`,
the `Node` struct would need two lifetime parameters.
But then the `next` field needs to be updated to
either `&'a Node<'b, 'b>` which still constraints lifetimes in a cycle to be the same,
or `&'a Node<'b, 'c>` which makes `Node` seem to need *three* lifetime parameters
and we’re back to types of infinite size.

One way to achieve same-lifetime is if the nodes are members of the same composite value,
such as a tuple:

```rust
use std::cell::Cell;
struct Node<'a> { value: u32, next: Cell<Option<&'a Node<'a>>> }

let (a, b, c) = (
    Node { value: 0, next: Cell::new(None) },
    Node { value: 7, next: Cell::new(None) },
    Node { value: 42, next: Cell::new(None) },
);

// Create a cycle between b and c:
a.next.set(Some(&b));
b.next.set(Some(&c));
c.next.set(Some(&b));

// Traverse the graph just to show it works:
let mut node = &a;
let mut values = Vec::new();
for _ in 0..10 {
    values.push(node.value);
    node = node.next.get().unwrap()
}
assert_eq!(values, [0, 7, 42, 7, 42, 7, 42, 7, 42, 7])
```

Hurray! We have a cycle with `&T` references in Rust.
But it’s not very useful yet:
this program hard-codes how many values are involves,
and creates them at the same time.

# A simple arena allocator, with `Vec` and `RefCell`

So we want to dynamically allocate a number of nodes to be owned by some shared storage,
and allow nodes to borrow each other from that storage.
The nodes will all be destroyed around the same time, when the storage is dropped.

This pattern has existed before Rust, it’s called an *arena allocator*.
Implementing it requires using some `unsafe` code,
but Rust’s borrowing enables us to make it provide a safe API
(by keeping it in a module so that other code cannot mess with its private fields).

Here a simple arena implementation, followed by some code using it similar to above.

```rust
use std::cell::RefCell;

pub struct Arena<T> {
    chunks: RefCell<Vec<Vec<T>>>,
}

impl<T> Arena<T> {
    pub fn new() -> Arena<T> {
        Arena {
            chunks: RefCell::new(vec![Vec::with_capacity(8)]),
        }
    }

    pub fn allocate(&self, value: T) -> &T {
        let mut chunks = self.chunks.borrow_mut();
        if chunks.last().unwrap().len() >= chunks.last().unwrap().capacity() {
            let new_capacity = chunks.last().unwrap().capacity() * 2;
            chunks.push(Vec::with_capacity(new_capacity))
        }
        chunks.last_mut().unwrap().push(value);
        let value_ptr: *const T = chunks.last().unwrap().last().unwrap();
        unsafe {
            // Unsafely dereference a raw pointer to artificially
            // extend the lifetime of the returned reference
            &*value_ptr
        }
    }
}

/////////////

use std::cell::Cell;
struct Node<'arena> { value: u32, next: Cell<Option<&'arena Node<'arena>>> }

// impl<'arena> Drop for Node<'arena> { fn drop(&mut self) {} }

let arena = Arena::new();
let c = arena.allocate(Node { value: 42, next: Cell::new(None) });
let b = arena.allocate(Node { value: 7, next: Cell::new(Some(c)) });
let a = arena.allocate(Node { value: 0, next: Cell::new(Some(b)) });

c.next.set(Some(b));

let mut node = a;
let mut values = Vec::new();
for _ in 0..10 {
    values.push(node.value);
    node = node.next.get().unwrap()
}
assert_eq!(values, [0, 7, 42, 7, 42, 7, 42, 7, 42, 7])
```

The idea is to keep `T` nodes in a `Vec<T>`,
and be careful to never to push beyond the initial capacity.
When a vector reaches its capacity, we create a new one
(growing them exponentially to amortize the allocation cost,
much like `Vec` itself would do if pushed beyond its capacity).
That way, the inner vectors of `T` are never reallocated,
and references to existing items stay valid.

The one `unsafe` block is small,
but its soundness relies on the entire module maintaining this invariant
of not moving already-allocated items.

# A faster arena, with raw pointers and `#[may_dangle]`

The arena implementation above isn’t bad (allocation is already *O(1)* amortized),
but it was written to be easy to read.
We can easily move things around to avoid for example redundant `.last().unwrap()` calls,
but calling `RefCell::borrow_mut` and `Vec::push` is still more work than strictly necessary.

In Rust an arena happens to enable ergonomic reference cycles,
but it is more typically used as a more efficient alternative to heap allocation.
If used in a tight loop, micro-optimizations can add up to be significant.
Ideally, the fast path of `Arena::allocate` (when the current chunk isn’t full yet)
would do nothing more than move the value and increment a pointer.

```rust,compile_fail
use std::cell::{Cell, RefCell};

pub struct Arena<T> {
    // Box<[T]> is similar to Vec<T> where len() == capacity()
    full_chunks: RefCell<Vec<Box<[T]>>>,

    // This has a different memory representation, but is equivalent to Vec<T>
    start: Cell<*mut T>,
    next: Cell<*mut T>,
    end: Cell<*mut T>,
}

impl<T> Arena<T> {
    pub fn new() -> Self {
        assert!(std::mem::size_of::<T>() != 0,
                "this arena cannot be used with zero-sized types");
        unimplemented!()
    }

    pub fn allocate(&self, item: T) -> &T {
        if self.next.get() == self.end.get() {
            self.new_chunk()
        }
        let next = self.next.get();
        unsafe {
            std::ptr::write(next, item);
            self.next.set(next.offset(1));
            &*next
        }
    }

    #[inline(never)]
    #[cold]
    fn new_chunk(&self) {
        unimplemented!()
        // Swap self.start/next/end with a new Vec<T>
        // and push the old (full) one to self.full_chunks.
    }
}

impl<T> Drop for Arena<T> {
    fn drop(&mut self) {
        unimplemented!()
        // Vec::from_raw_parts() based on self.start/next/end,
        // then let Vec::drop do its work.
    }
}

/////////////

struct Node<'arena> { value: u32, next: Cell<Option<&'arena Node<'arena>>> }

let arena = Arena::new();

// error[E0597]: `arena` does not live long enough
let a = arena.allocate(Node { value: 0, next: Cell::new(None) });
//      ^^^^^ borrowed value does not live long enough
let b = arena.allocate(Node { value: 7, next: Cell::new(Some(a)) });
//      ^^^^^ borrowed value does not live long enough
a.next.set(Some(b));

// `arena` dropped here while still borrowed
// note: values in a scope are dropped in the opposite order they are created
```

Some implementation details are left out as they’re not terribly important for this post.
But this much hopefully shows the idea… and the the compiler isn’t happy with it.

So what changed?

# Drop checking

Compared to our previous `Arena` type, this one explicitly implements `Drop`.
The `drop` method obviously has access to the fields of `self`,
so if a `&U` reference is reachable from there it must be valid.
(Even if this particular `Drop` impl happens not to access those references.)

In other words, the mere existence of a `Drop` impl affects borrow-checking.
This is called [drop-checking](https://doc.rust-lang.org/nomicon/dropck.html).

We would have a similar issue if `Node` itself implemented `Drop`:
some nodes in a cycles would necessarily be dropped after others,
and their `drop` method would “see” invalid `&Node` references.
In that case we can work around this limitation by only implementing `Drop`
on only some fields of `Node`, separate from those that contain references to other nodes.

For cases like `Arena` though, the language provides
[an escape hatch](https://rust-lang.github.io/rfcs/1327-dropck-param-eyepatch.html).
We need to make three changes:

* Add a `#[may_dangle]` attribute on the `T` type parameter of the `Drop` impl.
  This indicates that we opt into allowing `T` to contain dangling `&_` references.
* Change the `impl` keyword to `unsafe impl`,
  to recognize that it’s our responsibility to not access these references.
* Add a `feature` attribute to the crate to opt into using the two unstable features
  of attribute syntax on type parameters and of the `may_dangle` attribute itself,
  and use a Nightly version of Rust.
  These features are current as of Rust 1.25, but they might still change
  (or even be removed entirely).

```rust
#![feature(generic_param_attrs, dropck_eyepatch)]

pub struct Arena<T> {
    start: std::cell::Cell<*mut T>,
    // …
}

unsafe impl<#[may_dangle] T> Drop for Arena<T> {
    fn drop(&mut self) {
        // …
    }
}
```

Why didn’t we need this before, with `RefCell<Vec<Vec<T>>>`?
In fact we did.
`Vec` took care of it for us, [with `#[may_dangle]`
on its own `Drop` impl](https://github.com/rust-lang/rust/blob/1.24.0/src/liballoc/vec.rs#L2123).

The standard library is allowed to use unstable language features, even on Stable,
because it is always updated together with the compiler.

# Working around drop-checking on Rust Stable

So now we have an efficient arena allocator, but it works on Rust Nightly.
This isn’t great, especially for a library that might be used by other people.
Can we avoid using the unstable `#[may_dangle]` attribute?

The current rules of drop-checking are fairly conservative.
They kick in as soon as an `impl Drop` block is generic over some type parameter.
Of course we still want `Arena<T>` to be generic,
and we still want *a* `Drop` impl that needs to know how to destruct `T` items.
The trick is to have them separately,
and store a pointer to a concrete instance of a generic function:

```rust
use std::cell::{RefCell, Cell};
use std::mem;
use std::ptr;

pub struct Arena<T> {
    full_chunks: RefCell<Vec<Box<[T]>>>,
    current_chunk: PartiallyFullChunk,
}

// Not parameterized over `T`
struct PartiallyFullChunk {
    start: Cell<*mut u8>,
    next: Cell<*mut u8>,
    end: Cell<*mut u8>,
    drop: fn(&PartiallyFullChunk),
}

impl<T> Arena<T> {
    pub fn new() -> Self {
        assert!(mem::size_of::<T>() != 0, "this arena cannot be used with zero-sized types");
        Arena {
            full_chunks: RefCell::new(Vec::new()),
            current_chunk: PartiallyFullChunk {
                // An empty arena doesn’t allocate
                start: Cell::new(ptr::null_mut()),
                next: Cell::new(ptr::null_mut()),
                end: Cell::new(ptr::null_mut()),

                // Instanciate a generic function, but don’t call it (yet).
                // Only take a pointer to it.
                drop: drop_partially_full_chunk::<T>,
            }
        }
    }

    // …
}

// This function is generic over `T`…
fn drop_partially_full_chunk<T>(chunk: &PartiallyFullChunk) {
    unimplemented!()
}

// … but this Drop impl or the struct are not.
impl Drop for PartiallyFullChunk {
    fn drop(&mut self) {
        (self.drop)(self)
    }
}
```

This has some additional run-time cost:
storing an extra pointer per arena, and making one dynamic function call when dropping it.
However this cost should be small or negligible,
assuming that a typical program has few arenas (even if it has many nodes in them).

See [`victor/src/arena.rs`](
https://github.com/SimonSapin/victor/blob/824b6950027e42/victor/src/arena.rs)
for a full implementation with tests.

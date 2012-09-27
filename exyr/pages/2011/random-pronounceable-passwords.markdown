title: Random pronounceable passwords
published: 2011-02-11
tags: [passwords, snippets]
summary: |
    Using a sample text for statistics and Markov chains, we can generate
    passwords that are both random (and thus strong) and pronounceable
    (and thus easier to memorize.)

It is often advised that passwords should should be long (8 characters
is considered good) and contain various kinds of characters (not just lower-case
letters.) Such a password is stronger against dictionary or brute-force
attacks.

The strongest password would be a completely random one. Generating
one is quite easy:

    $ head -c 12 /dev/random | base64
    RU0aq07R9ZVK8LR1

However, such a password is very hard to memorize (at least for me.) It is also
not so easy to type.

I find that I remember words (and people’s names!) much better if I know
how to pronounce them. They
do not have to be pronounced out loud, I just remember the sound it would do
more than each individual letter. This means that a “pronounceable” password
 would be
much easier to memorize (at least for me, again.) Most words in most languages
are easy to pronounce so we could just pick one, but that’s a very weak
password against dictionary attacks. We need something random.

So, what is pronounceable? Real words that are hard to pronounce often have
many consecutive consonants. We could just alternate consonants and vowels,
that’s easy enough:

    :::python
    import random
    
    def pronounceable_password():
        # I omitted some letters I don’t like
        vowels = 'aiueo'
        consonants = 'bdfgjklmnprstvwxz'
        while 1:
            yield random.choice(consonants)
            yield random.choice(vowels)
            
    print ''.join(itertools.islice(pronounceable_password(), 14))
    
And a few results:

    bonugevazisibe
    wobumubidigato
    wuxarewuvidiri
    zixizuzugurete
    mejevefibawuso
    figosotufixaza

Not bad, but we can do better (and more interesting!)

The Japanese language is made of a well-known set of syllables (sounds), 
most of which consist of a consonant followed by a vowel when *romanized*
(written in Latin alphabet.) This is why Japanese is mostly easy to pronounce
for westerners, but many foreign words are distorted in Japanese. For example,
they use the international word “taxi”, but it’s pronounced more like
*ta-ku-shi*.

Anyway. Using [Markov chains](http://en.wikipedia.org/wiki/Markov_chain),
we can generate text that “sounds” Japanese. Markov chains have many
interesting mathematical properties but the basics is that they represent
a system that transits between states, and the next state depends only on the
current state and not the past. In other words, for text, each character has
a probability of being chosen that depends on the previous character.
To determine these probabilities, we look at pairs of consecutive characters
in a sample text.



The algorithm looks like this: (Also see the [complete
code](https://github.com/SimonSapin/snippets/blob/master/markov_passwords.py).)

    :::python    
    class MarkovChain(object):
        def __init__(self, sample):
            self.counts = counts = defaultdict(lambda: defaultdict(int))
            for current, next in pairwise(sample):
                counts[current][next] += 1
            
            self.totals = dict(
                (current, sum(next_counts.itervalues()))
                for current, next_counts in counts.iteritems()
            )
            

        def next(self, state):
            nexts = self.counts[state].iteritems()
            # Like random.choice() but with a different weight for each element
            rand = random.randrange(0, self.totals[state])
            for next_state, weight in nexts:
                if rand < weight:
                    return next_state
                rand -= weight

Again, a few resutlts:

    odauarabarikoy
    hitarikametata
    imarotamenayan
    abautiyosihere
    ukihumetotarit
    womitohinarego

This is subjective, but I like these better. (Could be because I’m learning
Japanese.)
Maybe considering the 2 or more previous characters instead of just one would
yield better results. This is left as an exercise for the reader ;)

This algorithm produces passwords with only lower-case letters which is 
generally considered a bad idea, but this is compensated by the length.
It also makes the password easier to type.

If we mix 26 lower case letters, as many upper case, ten digits and a dozen
of other symbols, that’s 72 possible characters. Picking 8 of them at random
gives 72<sup>8</sup> possible passwords, or about 49 bits of
[entropy](http://en.wikipedia.org/wiki/Entropy_%28information_theory%29).
It is possible to calculate the exact entropy for a Markov chain, but the math
is non-trivial. I guesstimated that this pseudo-japanese is about the same
entropy as alternating 15-something consonants with 5 vowels. So for
14-characters passwords, that’s 15<sup>7</sup> × 5<sup>7</sup> possible
passwords or about 43 bits of entropy; which I decided was good enough for me.

Now [grab the 
code](https://github.com/SimonSapin/snippets/blob/master/markov_passwords.py)
and go change all those weak passwords!

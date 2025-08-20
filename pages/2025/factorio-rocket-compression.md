title: "Factorio tool: rocket compression"
published: 2025-08-20
summary: |
    In Factorio Space Age, which items take more rocket to launch than their ingredients?

[Factorio](https://factorio.com/) is an automation and logistics game
where the player builds factories to collect resources, transform them into intermediate items,
assemble them into more complex items, etc.
The [Space Age](https://factorio.com/space-age/content) extension adds multiple planets,
with interplanetary logistics based on launching rockets carrying up to 1000 kg of cargo.
Each item has a fixed **weight** which determines how many can fit in one rocket:
the item’s rocket capacity.

Weights are chosen for game balance rather than for realism.
Each rocket launch has a cost;
in some cases it’s cheaper to launch ingredients and craft an item at the destination
than to launch the finished product.
This equation can change if some ingredients are easily available at the destination.

Internally, some weights are computed
with [a non-trivial formula](https://lua-api.factorio.com/latest/auxiliary/item-weight.html).
After [implementing it outside of the game](https://github.com/factoriolab/factoriolab/pull/1746)
we define the **weight compression** of every recipe as
the weight of its ingredients divided by the weight of its products.
Compression greater than 1 means it’s cheaper to launch finished products.

-----

<div id=tool><em>Loading…</em></div>
<script type=module src=tool.js></script>

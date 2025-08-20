// @ts-check

import van from "./van-1.5.5.min.js";
/** @import {ModData} from "./data.d.ts" */

//
// Data
//

const response = await fetch("./space-age-data.json");
if (!response.ok) {
  throw new Error(`Response status: ${response.status}`);
}
/** @type {ModData} */
const data = await response.json();

const items = Object.fromEntries(data.items.map((item) => [item.id, item]));
const recipes = data.recipes.filter(
  (recipe) =>
    // filter out: every flag except "locked",
    (recipe.flags ?? []).every((f) => f === "locked") &&
    // pseudo-recipes without any input,
    Object.keys(recipe.in).length > 0 &&
    // (un)barrelling,
    !recipe.id.endsWith("-barrel") &&
    // recipes with fluid ingredients or products that cannot be barelled
    Object.keys({ ...recipe.in, ...recipe.out }).every(
      (i) => items[i].stack || `${i}-barrel` in items
    )
);
// recipes.sort((a, b) => a.name.localeCompare(b.name));

//
// UI
//

const { link, style, p, span, input, table, colgroup, thead, tbody, tr, th, td, strong } = van.tags;

const iconWithName = (itemOrRecipe) => [
  span({ class: `icon icon-${itemOrRecipe.icon || itemOrRecipe.id}` }),
  " ",
  itemOrRecipe.name,
];

const icon = (itemOrRecipe) =>
  span(
    { class: `icon icon-${itemOrRecipe.icon || itemOrRecipe.id}`, title: itemOrRecipe.name },
    itemOrRecipe.name
  );

const formatWeight = (weight) => `${Math.ceil(weight * 10) / 10} kg`;

const weightCell = (formattedWeight, bold) =>
  td({ class: "data weight" }, bold ? strong(formattedWeight) : formattedWeight);

const itemList = (itemAmounts, padTo) => {
  const components = [];
  const entries = Object.entries(itemAmounts);
  const cells = entries.map(([id, amount]) => {
    const checked = van.state(true);
    const checkbox =
      entries.length > 1
        ? td(
            input({
              type: "checkbox",
              checked: true,
              onclick: (e) => (checked.val = e.target.checked),
            })
          )
        : td();
    amount = Math.round(amount * 10000) / 10000;
    const item = items[id];
    const itemCell = td({ class: "data" }, icon(item), " ", amount);
    const barrelItem = items[`${id}-barrel`];
    const shipmentCell = item.stack
      ? itemCell
      : td({ class: "data" }, icon(barrelItem), " ", amount / 50);
    const fluidCell = item.stack ? td() : itemCell;
    const cap = item.stack ? item.rocketCapacity || 0 : (barrelItem?.rocketCapacity || 0) * 50;
    const weight = (amount * 1000) / cap;
    components.push([checked, weight]);
    const bold = padTo == 1;
    return [weightCell(formatWeight(weight), bold), checkbox, shipmentCell, fluidCell];
  });
  for (const _ of Array(padTo - entries.length)) {
    cells.push([td(), td(), td(), td()]);
  }
  const total = van.derive(() =>
    components.reduce((acc, [checked, weight]) => (checked.val ? acc + weight : acc), 0)
  );
  if (padTo > 1) {
    const formattedTotal = van.derive(() => formatWeight(total.val));
    cells.push([weightCell(formattedTotal, true), td(), td(), td()]);
  }
  return { cells, total };
};

const searchTerm = van.state("");

const elements = [
  link({ rel: "stylesheet", href: "style.css" }),
  style(
    data.icons
      .map((icon) => `.icon-${icon.id}::before { background-position: ${icon.position} }\n`)
      .join("")
  ),
  p(
    "🔎︎ ",
    input({
      placeholder: "Filter by recipe name",
      oninput: (e) => (searchTerm.val = e.target.value.toLowerCase()),
    })
  ),
  table(
    colgroup({ span: 1 }),
    colgroup({ span: 1, class: "inner-column" }),
    colgroup({ span: 4, class: "inner-column" }),
    colgroup({ span: 4 }),
    thead(
      tr(
        th("Recipe"),
        th("Comp."),
        th({ colspan: 4 }, "Ingredients"),
        th({ colspan: 4 }, "Products")
      )
    ),
    recipes.map((recipe, i) => {
      const ingredients = Object.keys(recipe.in);
      const products = Object.keys(recipe.out);
      const max = Math.max(ingredients.length, products.length);
      // additional row for the total weight
      const rowSpan = max == 1 ? 1 : max + 1;
      const { cells: iCells, total: iWeight } = itemList(recipe.in, max);
      const { cells: pCells, total: pWeight } = itemList(recipe.out, max);
      const [firstIngredient, ...otherIngredients] = iCells;
      const [firstProduct, ...otherProducts] = pCells;
      return tbody(
        { hidden: () => !recipe.name.toLowerCase().includes(searchTerm.val) },
        tr(
          td({ rowSpan }, iconWithName(recipe)),
          td({ rowSpan }, strong(van.derive(() => (iWeight.val / pWeight.val).toFixed(2)))),
          firstIngredient,
          firstProduct
        ),
        ...Array.from(Array(rowSpan - 1), (_, i) => tr(otherIngredients[i], otherProducts[i]))
      );
    })
  ),
];

//
// Install
//

const tool = document.getElementById("tool");
if (!tool) {
  throw new Error();
}
tool.replaceChildren(...elements);

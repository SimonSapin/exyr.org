export interface ModData {
  version: Entities;
  categories: CategoryJson[];
  icons: IconJson[];
  items: ItemJson[];
  recipes: RecipeJson[];
  limitations?: Entities<string[]>;
  locations?: CategoryJson[];
  defaults?: DefaultsJson;
}

export type Entities<T = string> = Record<string, T>;

export interface CategoryJson {
  id: string;
  name: string;
  /** Used to link the category to an alternate icon id */
  icon?: string;
  /** Used to add extra text to an already defined icon */
  iconText?: string;
}

export interface IconJson {
  id: string;
  position: string;
  color: string;
  /** If true, icon is mostly white, and should be inverted in light mode */
  invertLight?: boolean;
}

export interface ItemJson {
  id: string;
  name: string;
  category: string;
  row: number;
  stack?: number;
  rocketCapacity?: number;
  beacon?: BeaconJson;
  belt?: BeltJson;
  pipe?: BeltJson;
  machine?: MachineJson;
  module?: ModuleJson;
  fuel?: FuelJson;
  cargoWagon?: CargoWagonJson;
  fluidWagon?: FluidWagonJson;
  technology?: TechnologyJson;
  /** Used to link the item to an alternate icon id */
  icon?: string;
  /** Used to add extra text to an already defined icon */
  iconText?: string;
}

export interface RecipeJson {
  id: string;
  name: string;
  category: string;
  row: number;
  time: number | string;
  producers: string[];
  in: ItemAmounts;
  out: ItemAmounts;
  /** Denotes amount of output that is not affected by productivity */
  catalyst?: Entities<number | string>;
  cost?: number | string;
  /** If recipe is a rocket launch, indicates the rocket part recipe used */
  part?: string;
  /** Used to link the recipe to an alternate icon id */
  icon?: string;
  /** Used to add extra text to an already defined icon */
  iconText?: string;
  /** Used to override the machine's usage for this recipe */
  usage?: number | string;
  disallowedEffects?: ModuleEffect[];
  locations?: string[];
  flags?: RecipeFlag[];
}

// NOTE(SimonSapin): Factoriolab uses `Entities<number | string>` here
// but strings are never used in Space Age data
export type ItemAmounts = Entities<number>;

export type RecipeFlag =
  | "mining"
  | "technology"
  | "burn"
  | "grow"
  | "recycling"
  | "locked"
  | "hideProducer";

export interface BeaconJson {
  effectivity: number | string;
  modules: number | string;
  range?: number | string;
  /** Beacons must use electric energy source, if any */
  type?: EnergyType.Electric;
  /** Energy consumption in kW */
  usage?: number | string;
  disallowedEffects?: ModuleEffect[];
  /** Width and height in tiles (integers, unless off-grid entity like tree) */
  size?: [number, number];
  profile?: number[];
}

export enum EnergyType {
  Burner = "burner",
  Electric = "electric",
}

export interface BeltJson {
  speed: number | string;
}

export interface MachineJson {
  /** If undefined, speed is based on belt speed */
  speed?: number | string;
  modules?: number | true;
  disallowedEffects?: ModuleEffect[];
  type?: EnergyType;
  /** Fuel categories, e.g. chemical or nuclear */
  fuelCategories?: string[];
  /** Indicates a specific fuel that must be used */
  fuel?: string;
  /** Energy consumption in kW */
  usage?: number | string;
  /** Drain in kW */
  drain?: number | string;
  /** Pollution in #/m */
  pollution?: number | string;
  silo?: SiloJson;
  consumption?: Entities<number | string>;
  /** Width and height in tiles (integers, unless off-grid entity like tree) */
  size?: [number, number];
  /** Bonus effects that this machine always has */
  baseEffect?: Partial<Record<ModuleEffect, number>>;
  /** If true, hide the calculated number of machines */
  hideRate?: boolean;
  /** If true, tally totals by recipe instead of machine */
  totalRecipe?: boolean;
  /** Type of machine. (e.g. mining drill, assembling machine, etc) */
  entityType?: string;
  locations?: string[];
  /** Percent of ingredients used (Space Age: Biolab) */
  ingredientUsage?: number;
}

export interface ModuleJson {
  consumption?: number | string;
  pollution?: number | string;
  productivity?: number | string;
  quality?: number | string;
  speed?: number | string;
  limitation?: string;
  sprays?: number;
  proliferator?: string;
}

export type ModuleEffect = "consumption" | "pollution" | "productivity" | "quality" | "speed";

export interface FuelJson {
  category: string;
  /** Fuel value in MJ */
  value: number | string;
  result?: string;
}

export interface CargoWagonJson {
  size: number | string;
}

export interface FluidWagonJson {
  capacity: number | string;
}

export interface SiloJson {
  /** Number of rocket parts required */
  parts: number | string;
  /** Launch animation delay, in ticks */
  launch: number | string;
}

export interface TechnologyJson {
  prerequisites?: string[];
  unlockedRecipes?: string[];

  // IDs of recipes that get a 10% productivity bonus for every level of this technology
  prodUpgrades?: string[];
}

export type DefaultsJson = HardCodedPresetsJson | CustomPresetsJson;

export interface HardCodedPresetsJson {
  beacon?: string;
  minBelt?: string;
  maxBelt?: string;
  minPipe?: string;
  maxPipe?: string;
  fuelRank?: string[];
  cargoWagon?: string;
  fluidWagon?: string;
  excludedRecipes?: string[];
  minMachineRank?: string[];
  maxMachineRank?: string[];
  moduleRank?: string[];
  beaconModule?: string;
}

export interface CustomPresetsJson {
  presets: PresetJson[];

  // Defaults for corresponding `DefaultsPresetJson` properties:
  locations?: string[];
  belt?: string;
  beltStack?: number | string;
  pipe?: string;
  fuelRank?: string[];
  cargoWagon?: string;
  fluidWagon?: string;
  excludedRecipes?: string[];
  machineRank?: string[];
  moduleRank?: string[];
  beacon?: string;
  beaconModule?: string;
}

export interface PresetJson {
  /**
   * ID in `src/assets/i18n/*.json`
   * Example: "options.preset.minimum"
   */
  id: number;
  label: string;

  locations?: string[];
  belt?: string;
  beltStack?: number | string;
  pipe?: string;
  fuelRank?: string[];
  cargoWagon?: string;
  fluidWagon?: string;
  excludedRecipes?: string[];
  machineRank?: string[];
  moduleRank?: string[];
  beacon?: string;
  beaconModule?: string;

  /** Defaults to zero */
  beaconCount?: number | string;
}

# Object Catalog Reference

The full object catalog is at `assets/objects/object_catalog.json` (24 objects). Read it to get exact names, dimensions, and USD paths.

## Catalog Entry Format

Each entry has:
```json
{
  "name": "banana",           // prim name used in scene
  "usd_path": "assets/objects/ycb/banana.usd",  // relative path to USD file
  "class": "fruit",           // object category
  "description": "A yellow banana",
  "dims": [0.19, 0.04, 0.04] // bounding box [x, y, z] in meters
}
```

## Object Classes

Use the exact names and paths in the catalog. The retained collection includes:

| Category | Objects |
|---|---|
| Blocks and toys | blue_block, green_block, red_block, yellow_block, rubiks_cube |
| Fruit | banana, lemon_01, orange_01 |
| Containers and dishware | bowl, mug, pitcher, clay_plates |
| Bottles and condiments | bbq_sauce_bottle, mustard, soft_scrub |
| Boxes and cans | sugar_box, coffee_can, tomato_soup_can |
| Utensils and tools | spoon, scissors, cordless_drill |
| Desktop items | dry_erase_marker, remote_control, computer_mouse |

## Important Notes

- Object `name` must match exactly when used in scenes and tasks
- `dims` are in meters — use these to compute placement spacing
- `usd_path` is relative to the repo root
- For scene USDA, the payload path must be relative to `assets/scenes/` (e.g., `@../objects/ycb/banana.usd@`)

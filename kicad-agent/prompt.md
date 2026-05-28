# KiCad Agent -- Operation Reference

This reference documents all operations supported by kicad-agent. Claude uses these schemas to construct valid JSON operations that the Python backend validates and executes against KiCad files.

**Key principle:** The LLM never touches raw S-expressions. It emits structured JSON intents, and the Python tool layer mutates the AST, serializes valid KiCad files, and validates via ERC/DRC gates.

**Supported file types:** `.kicad_sch` (schematic), `.kicad_pcb` (PCB), `.kicad_sym` (symbol library), `.kicad_mod` (footprint library)

**KiCad version:** 10+ only

---

## Available Operations

### Component Operations

#### add_component

Add a component to a schematic or PCB.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"add_component"` |
| `target_file` | string | Relative path to KiCad file (`.kicad_sch` or `.kicad_pcb`) |
| `library_id` | string | Library reference, e.g. `"Device:R_Small_US"` (1-256 chars) |
| `position` | object | Placement coordinates `{x, y}` with optional `angle` (degrees, default 0) |

**Optional fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `reference` | string | `"R?"` | Reference designator (1-64 chars) |
| `value` | string | `""` | Component value (max 256 chars) |

**Example:**

```json
{
  "root": {
    "op_type": "add_component",
    "target_file": "motor-driver.kicad_sch",
    "library_id": "Device:R_Small_US",
    "reference": "R1",
    "value": "10k",
    "position": {"x": 50.0, "y": 30.0, "angle": 90.0}
  }
}
```

---

#### remove_component

Remove a component by reference designator.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"remove_component"` |
| `target_file` | string | Relative path to KiCad file |
| `reference` | string | Reference designator to remove (1-64 chars) |

**Example:**

```json
{
  "root": {
    "op_type": "remove_component",
    "target_file": "motor-driver.kicad_sch",
    "reference": "R1"
  }
}
```

---

#### move_component

Move a component to a new position.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"move_component"` |
| `target_file` | string | Relative path to KiCad file |
| `reference` | string | Reference designator of the component to move (1-64 chars) |
| `position` | object | Target coordinates `{x, y}` with optional `angle` |

**Example:**

```json
{
  "root": {
    "op_type": "move_component",
    "target_file": "motor-driver.kicad_pcb",
    "reference": "U3",
    "position": {"x": 100.0, "y": 50.0, "angle": 180.0}
  }
}
```

---

#### modify_property

Modify a component property (value, footprint, reference, custom field).

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"modify_property"` |
| `target_file` | string | Relative path to KiCad file |
| `reference` | string | Reference designator (1-64 chars) |
| `property_name` | string | Property to modify, e.g. `"Value"`, `"Footprint"` (1-128 chars) |
| `new_value` | string | New property value (max 1024 chars) |

**Example:**

```json
{
  "root": {
    "op_type": "modify_property",
    "target_file": "motor-driver.kicad_sch",
    "reference": "R1",
    "property_name": "Value",
    "new_value": "4.7k"
  }
}
```

---

#### duplicate_component

Duplicate a component with fresh UUID and incremented reference.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"duplicate_component"` |
| `target_file` | string | Relative path to KiCad file |
| `source_reference` | string | Reference designator of the component to duplicate (1-64 chars) |

**Optional fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `offset` | object | `null` | Position offset from source `{x, y}` (angle ignored) |
| `count` | integer | `1` | Number of copies (1-100) |

**Example:**

```json
{
  "root": {
    "op_type": "duplicate_component",
    "target_file": "motor-driver.kicad_sch",
    "source_reference": "R1",
    "offset": {"x": 5.0, "y": 0.0},
    "count": 3
  }
}
```

---

#### array_replicate

Replicate a component in a linear, circular, or matrix array pattern.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"array_replicate"` |
| `target_file` | string | Relative path to KiCad file |
| `source_reference` | string | Reference designator of the component to replicate (1-64 chars) |
| `pattern` | string | Array pattern: `"linear"`, `"circular"`, or `"matrix"` |
| `spacing` | object | Position spacing `{x, y}` with optional `angle` |

**Optional fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `count` | integer | `1` | Number of replications (1-100) |
| `angle_step` | number | `null` | Degrees per step (circular pattern only) |
| `center` | object | `null` | Center point `{x, y}` (circular pattern only) |
| `rows` | integer | `null` | Number of rows (matrix pattern only) |
| `cols` | integer | `null` | Number of columns (matrix pattern only) |

**Example (linear):**

```json
{
  "root": {
    "op_type": "array_replicate",
    "target_file": "motor-driver.kicad_sch",
    "source_reference": "R1",
    "pattern": "linear",
    "count": 4,
    "spacing": {"x": 5.0, "y": 0.0}
  }
}
```

**Example (matrix):**

```json
{
  "root": {
    "op_type": "array_replicate",
    "target_file": "motor-driver.kicad_pcb",
    "source_reference": "LED1",
    "pattern": "matrix",
    "spacing": {"x": 3.0, "y": 3.0},
    "rows": 3,
    "cols": 4
  }
}
```

---

### Net Operations

#### add_net

Add a net to a PCB.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"add_net"` |
| `target_file` | string | Relative path to KiCad PCB file (`.kicad_pcb`) |

**Optional fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `net_name` | string | `""` | Net name. Empty triggers auto-generation as `N_<number>` (max 64 chars) |
| `net_number` | integer | `null` | Explicit net number. `null` = auto-assign |

**Example:**

```json
{
  "root": {
    "op_type": "add_net",
    "target_file": "motor-driver.kicad_pcb",
    "net_name": "VCC_3V3"
  }
}
```

---

#### remove_net

Remove a net from a PCB, disconnecting all pads.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"remove_net"` |
| `target_file` | string | Relative path to KiCad PCB file |
| `net_name` | string | Name of the net to remove (1-64 chars) |

**Example:**

```json
{
  "root": {
    "op_type": "remove_net",
    "target_file": "motor-driver.kicad_pcb",
    "net_name": "VCC_3V3"
  }
}
```

---

#### rename_net

Rename a net, propagating to all connected pads.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"rename_net"` |
| `target_file` | string | Relative path to KiCad PCB file |
| `old_name` | string | Current net name (1-64 chars) |
| `new_name` | string | Desired new net name (1-64 chars) |

**Example:**

```json
{
  "root": {
    "op_type": "rename_net",
    "target_file": "motor-driver.kicad_pcb",
    "old_name": "VCC_3V3",
    "new_name": "VCC_3V3_DIGITAL"
  }
}
```

---

### Bus Operations

#### add_bus

Add a bus to a schematic with member nets.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"add_bus"` |
| `target_file` | string | Relative path to KiCad schematic file (`.kicad_sch`) |
| `bus_name` | string | Bus name (1-64 chars) |
| `member_nets` | array | List of net names that belong to this bus (1-32 members, each max 64 chars) |

**Example:**

```json
{
  "root": {
    "op_type": "add_bus",
    "target_file": "motor-driver.kicad_sch",
    "bus_name": "SPI_BUS",
    "member_nets": ["SPI_MOSI", "SPI_MISO", "SPI_SCK", "SPI_CS"]
  }
}
```

---

#### remove_bus

Remove a bus from a schematic.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"remove_bus"` |
| `target_file` | string | Relative path to KiCad schematic file |
| `bus_name` | string | Bus name to remove (1-64 chars) |

**Example:**

```json
{
  "root": {
    "op_type": "remove_bus",
    "target_file": "motor-driver.kicad_sch",
    "bus_name": "SPI_BUS"
  }
}
```

---

### Reference Operations

#### renumber_refs

Renumber component references with configurable prefix and sequencing.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"renumber_refs"` |
| `target_file` | string | Relative path to KiCad schematic file |

**Optional fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `prefix` | string | `""` | Only renumber components with this prefix. Empty = all (max 16 chars) |
| `start_index` | integer | `1` | Starting index for numbering (min 1) |
| `step` | integer | `1` | Step between sequential indices (min 1) |

**Example:**

```json
{
  "root": {
    "op_type": "renumber_refs",
    "target_file": "motor-driver.kicad_sch",
    "prefix": "R",
    "start_index": 1,
    "step": 1
  }
}
```

---

#### validate_refs

Validate that all component references are unique.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"validate_refs"` |
| `target_file` | string | Relative path to KiCad schematic file |

**Example:**

```json
{
  "root": {
    "op_type": "validate_refs",
    "target_file": "motor-driver.kicad_sch"
  }
}
```

---

#### annotate

Auto-assign references to unannotated components (refs ending in `?`).

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"annotate"` |
| `target_file` | string | Relative path to KiCad schematic file |

**Optional fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `prefix_filter` | string | `""` | Only annotate components matching this prefix. Empty = all (max 16 chars) |

**Example:**

```json
{
  "root": {
    "op_type": "annotate",
    "target_file": "motor-driver.kicad_sch",
    "prefix_filter": "R"
  }
}
```

---

#### cross_ref_check

Verify all symbol libIds resolve to entries in the embedded libSymbols.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"cross_ref_check"` |
| `target_file` | string | Relative path to KiCad schematic file |

**Example:**

```json
{
  "root": {
    "op_type": "cross_ref_check",
    "target_file": "motor-driver.kicad_sch"
  }
}
```

---

### Footprint Operations

#### assign_footprint

Assign a footprint to a schematic component.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"assign_footprint"` |
| `target_file` | string | Relative path to KiCad schematic file |
| `reference` | string | Component reference designator, e.g. `"U1"` (1-64 chars) |
| `footprint_lib_id` | string | Footprint library reference, e.g. `"Package_DIP:DIP-8_W7.62mm"` (1-256 chars) |

**Example:**

```json
{
  "root": {
    "op_type": "assign_footprint",
    "target_file": "motor-driver.kicad_sch",
    "reference": "U1",
    "footprint_lib_id": "Package_DIP:DIP-8_W7.62mm"
  }
}
```

---

#### swap_footprint

Swap a PCB footprint while preserving pad-to-net connections.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"swap_footprint"` |
| `target_file` | string | Relative path to KiCad PCB file |
| `reference` | string | Reference designator of the footprint to swap (1-64 chars) |
| `new_footprint_lib_id` | string | New footprint library reference (1-256 chars) |

**Example:**

```json
{
  "root": {
    "op_type": "swap_footprint",
    "target_file": "motor-driver.kicad_pcb",
    "reference": "U3",
    "new_footprint_lib_id": "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"
  }
}
```

---

#### validate_footprint

Validate that a footprint exists in the available libraries.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"validate_footprint"` |
| `target_file` | string | Relative path to KiCad file |
| `footprint_lib_id` | string | Footprint library reference to validate (1-256 chars) |

**Example:**

```json
{
  "root": {
    "op_type": "validate_footprint",
    "target_file": "motor-driver.kicad_pcb",
    "footprint_lib_id": "Package_DIP:DIP-8_W7.62mm"
  }
}
```

---

#### verify_pin_map

Verify that symbol pin numbers match footprint pad numbers.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"verify_pin_map"` |
| `target_file` | string | Relative path to KiCad file |
| `reference` | string | Component reference designator (1-64 chars) |
| `footprint_lib_id` | string | Footprint library reference to verify against (1-256 chars) |

**Example:**

```json
{
  "root": {
    "op_type": "verify_pin_map",
    "target_file": "motor-driver.kicad_sch",
    "reference": "U1",
    "footprint_lib_id": "Package_DIP:DIP-8_W7.62mm"
  }
}
```

---

#### update_footprint_from_library

Reload a PCB footprint's geometry from the library `.kicad_mod` file, preserving position, rotation, net assignments, reference designator, and PCB-embedded fields (UUID, path, sheetname, sheetfile). Equivalent to KiCad's "Update Footprints from Library" GUI command. Fixes `lib_footprint_mismatch` DRC violations.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"update_footprint_from_library"` |
| `target_file` | string | Relative path to KiCad PCB file (`.kicad_pcb` only) |
| `reference` | string | Reference designator of the footprint to update (1-64 chars) |

**Optional fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `footprint_lib_id` | string | `null` | Override lib_id. `null` = refresh from existing library (1-256 chars) |

**Example (refresh from existing library):**

```json
{
  "root": {
    "op_type": "update_footprint_from_library",
    "target_file": "board.kicad_pcb",
    "reference": "U2"
  }
}
```

**Example (swap and update in one step):**

```json
{
  "root": {
    "op_type": "update_footprint_from_library",
    "target_file": "board.kicad_pcb",
    "reference": "U3",
    "footprint_lib_id": "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"
  }
}
```

**Result details:**

```json
{
  "reference": "U2",
  "lib_id": "Package_TO_SOT_SMD:SOT-223-3_TabPin2",
  "old_lib_id": "Package_TO_SOT_SMD:SOT-223-3_TabPin2",
  "preserved_nets": 3,
  "lost_nets": [],
  "new_pads": []
}
```

- `preserved_nets`: Number of pad-to-net connections successfully transferred to the new footprint
- `lost_nets`: Pad numbers whose nets couldn't be restored (pad doesn't exist in new footprint)
- `new_pads`: Pad numbers in the new footprint that weren't in the old one

---

### Schematic Connectivity

#### add_wire

Add a wire segment between two points in a schematic.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"add_wire"` |
| `target_file` | string | Relative path to KiCad schematic file (`.kicad_sch`) |
| `start_x` | number | Start X coordinate in mm |
| `start_y` | number | Start Y coordinate in mm |
| `end_x` | number | End X coordinate in mm |
| `end_y` | number | End Y coordinate in mm |

**Example:**

```json
{
  "root": {
    "op_type": "add_wire",
    "target_file": "filter.kicad_sch",
    "start_x": 50.0,
    "start_y": 30.0,
    "end_x": 70.0,
    "end_y": 30.0
  }
}
```

---

#### add_label

Add a net label to a schematic (local, global, or hierarchical).

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"add_label"` |
| `target_file` | string | Relative path to KiCad schematic file (`.kicad_sch`) |
| `name` | string | Label text (1-128 chars, e.g. `"SDA"`, `"+5V"`) |
| `position` | object | Placement coordinates `{x, y}` with optional `angle` |

**Optional fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `label_type` | string | `"local"` | Label scope: `"local"`, `"global"`, or `"hierarchical"` |
| `shape` | string | `"input"` | Shape for global/hierarchical labels: `"input"`, `"output"`, `"bidirectional"`, `"tri_state"`, `"passive"` |

**Example:**

```json
{
  "root": {
    "op_type": "add_label",
    "target_file": "filter.kicad_sch",
    "name": "SDA",
    "label_type": "local",
    "position": {"x": 50.0, "y": 30.0},
    "shape": "input"
  }
}
```

---

#### add_power

Add a power symbol to a schematic (e.g. +5V, GND, +3V3). Places a `power:<name>` library symbol with a single pin that connects to the named net.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"add_power"` |
| `target_file` | string | Relative path to KiCad schematic file (`.kicad_sch`) |
| `name` | string | Power net name (1-64 chars, e.g. `"+5V"`, `"GND"`, `"+3V3"`) |
| `position` | object | Placement coordinates `{x, y}` with optional `angle` |

**Example:**

```json
{
  "root": {
    "op_type": "add_power",
    "target_file": "filter.kicad_sch",
    "name": "+12V",
    "position": {"x": 20.0, "y": 50.0}
  }
}
```

---

#### add_no_connect

Add a no-connect flag to a schematic pin.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"add_no_connect"` |
| `target_file` | string | Relative path to KiCad schematic file (`.kicad_sch`) |
| `position` | object | Placement coordinates `{x, y}` (angle is ignored) |

**Example:**

```json
{
  "root": {
    "op_type": "add_no_connect",
    "target_file": "filter.kicad_sch",
    "position": {"x": 86.36, "y": 317.5}
  }
}
```

---

#### add_junction

Add a junction dot at a wire intersection in a schematic.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"add_junction"` |
| `target_file` | string | Relative path to KiCad schematic file (`.kicad_sch`) |
| `position` | object | Placement coordinates `{x, y}` (angle is ignored) |

**Example:**

```json
{
  "root": {
    "op_type": "add_junction",
    "target_file": "filter.kicad_sch",
    "position": {"x": 50.0, "y": 30.0}
  }
}
```

---

### Library Management

#### add_lib_entry

Add a library entry to sym-lib-table or fp-lib-table.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"add_lib_entry"` |
| `target_file` | string | Relative path to sym-lib-table or fp-lib-table |
| `lib_name` | string | Library name (1-128 chars, e.g. `"Device"`, `"MyLib"`) |
| `lib_type` | string | Library type: `"KiCad"` or `"Legacy"` |
| `uri` | string | Library URI path (1-512 chars, may contain `${KIPRJMOD}`) |

**Optional fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `options` | string | `""` | Library options string |
| `description` | string | `""` | Library description |

**Example:**

```json
{
  "root": {
    "op_type": "add_lib_entry",
    "target_file": "sym-lib-table",
    "lib_name": "MyLib",
    "lib_type": "KiCad",
    "uri": "${KIPRJMOD}/MyLib.kicad_sym"
  }
}
```

---

#### remove_lib_entry

Remove a library entry from sym-lib-table or fp-lib-table.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"remove_lib_entry"` |
| `target_file` | string | Relative path to sym-lib-table or fp-lib-table |
| `lib_name` | string | Library name to remove (1-128 chars) |

**Example:**

```json
{
  "root": {
    "op_type": "remove_lib_entry",
    "target_file": "sym-lib-table",
    "lib_name": "MyLib"
  }
}
```

---

### Validation & Repair

#### repair_schematic

Auto-repair common ERC errors: wire snapping, orphaned label removal, no-connect placement.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"repair_schematic"` |
| `target_file` | string | Relative path to KiCad schematic file (`.kicad_sch`) |

**Optional fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `snap_wires` | boolean | `true` | Snap wire endpoints to nearest pin positions |
| `remove_orphans` | boolean | `true` | Remove labels not connected to any wire or pin |
| `place_no_connects` | boolean | `true` | Place no-connect markers on unconnected pins |

**Example:**

```json
{
  "root": {
    "op_type": "repair_schematic",
    "target_file": "filter.kicad_sch"
  }
}
```

---

#### validate_power_nets

Check all power pins have connected power symbols. Validates every `power_in`/`power_out` pin is connected to a `power:*` library reference.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"validate_power_nets"` |
| `target_file` | string | Relative path to KiCad schematic file (`.kicad_sch`) |

**Example:**

```json
{
  "root": {
    "op_type": "validate_power_nets",
    "target_file": "filter.kicad_sch"
  }
}
```

---

### PCB Design

#### add_copper_zone

Add a copper zone/ground pour to a PCB.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"add_copper_zone"` |
| `target_file` | string | Relative path to KiCad PCB file (`.kicad_pcb`) |
| `net_name` | string | Net name for the zone (1-64 chars, e.g. `"GND"`) |

**Optional fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `layer` | string | `"F.Cu"` | Copper layer (e.g. `"F.Cu"`, `"B.Cu"`) |
| `clearance` | number | `0.5` | Zone clearance in mm (> 0) |
| `min_width` | number | `0.25` | Minimum fill width in mm (> 0) |
| `priority` | integer | `0` | Zone priority (higher = filled first) |

**Example:**

```json
{
  "root": {
    "op_type": "add_copper_zone",
    "target_file": "board.kicad_pcb",
    "net_name": "GND",
    "layer": "B.Cu"
  }
}
```

---

#### set_board_outline

Define PCB board shape as a rectangle on Edge.Cuts.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"set_board_outline"` |
| `target_file` | string | Relative path to KiCad PCB file (`.kicad_pcb`) |
| `width` | number | Board width in mm (> 0, max 1000) |
| `height` | number | Board height in mm (> 0, max 1000) |

**Example:**

```json
{
  "root": {
    "op_type": "set_board_outline",
    "target_file": "board.kicad_pcb",
    "width": 100.0,
    "height": 80.0
  }
}
```

---

#### add_net_class

Add a net class with track/via/clearance dimensions to a `.kicad_dru` file.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"add_net_class"` |
| `target_file` | string | Relative path to `.kicad_dru` file |
| `name` | string | Net class name (1-64 chars) |
| `clearance` | number | Clearance in mm (> 0) |
| `track_width` | number | Track width in mm (> 0) |
| `via_diameter` | number | Via diameter in mm (> 0) |
| `via_drill` | number | Via drill in mm (> 0) |

**Example:**

```json
{
  "root": {
    "op_type": "add_net_class",
    "target_file": "board.kicad_dru",
    "name": "Power",
    "clearance": 0.3,
    "track_width": 0.5,
    "via_diameter": 0.8,
    "via_drill": 0.4
  }
}
```

---

#### add_design_rule

Add a custom DRC rule to a `.kicad_dru` file.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"add_design_rule"` |
| `target_file` | string | Relative path to `.kicad_dru` file |
| `name` | string | Rule name (1-128 chars) |
| `constraint_type` | string | Constraint type (1-64 chars, e.g. `"clearance"`, `"width"`) |

**Optional fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `constraint_values` | object | `{}` | Key-value constraint parameters |
| `condition` | string | `""` | KiCad condition expression (max 512 chars) |

**Example:**

```json
{
  "root": {
    "op_type": "add_design_rule",
    "target_file": "board.kicad_dru",
    "name": "clearance_to_power",
    "constraint_type": "clearance",
    "constraint_values": {"min": "0.5"},
    "condition": "A.hasNetClass('Power')"
  }
}
```

---

#### assign_net_class

Assign a net class to a specific net in the PCB.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"assign_net_class"` |
| `target_file` | string | Relative path to KiCad PCB file (`.kicad_pcb`) |
| `net_name` | string | Net name (1-64 chars) |
| `net_class_name` | string | Net class name (1-64 chars) |

**Example:**

```json
{
  "root": {
    "op_type": "assign_net_class",
    "target_file": "board.kicad_pcb",
    "net_name": "VCC",
    "net_class_name": "Power"
  }
}
```

---

#### auto_route

Auto-route nets on a PCB using A* pathfinding.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"auto_route"` |
| `target_file` | string | Relative path to KiCad PCB file (`.kicad_pcb`) |

**Optional fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `nets` | array | `[]` | Specific net names to route (empty = route all) |
| `layer` | string | `"F.Cu"` | Target copper layer |

**Example:**

```json
{
  "root": {
    "op_type": "auto_route",
    "target_file": "board.kicad_pcb",
    "nets": ["SDA", "SCL"],
    "layer": "F.Cu"
  }
}
```

---

### File Creation

#### create_schematic

Create a new empty `.kicad_sch` file.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"create_schematic"` |
| `target_file` | string | Relative path for the new file (must not exist) |

**Optional fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `paper` | string | `"A4"` | Paper size (e.g. `"A4"`, `"A3"`) |
| `title` | string | `""` | Title block title |

**Example:**

```json
{
  "root": {
    "op_type": "create_schematic",
    "target_file": "new.kicad_sch",
    "paper": "A3",
    "title": "My Schematic"
  }
}
```

---

#### create_pcb

Create a new empty `.kicad_pcb` file.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"create_pcb"` |
| `target_file` | string | Relative path for the new file (must not exist) |

**Optional fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `title` | string | `""` | Title block title |

**Example:**

```json
{
  "root": {
    "op_type": "create_pcb",
    "target_file": "new.kicad_pcb",
    "title": "My Board"
  }
}
```

---

#### create_project

Create a new empty `.kicad_pro` project file.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"create_project"` |
| `target_file` | string | Relative path for the new file (must not exist) |

**Example:**

```json
{
  "root": {
    "op_type": "create_project",
    "target_file": "new.kicad_pro"
  }
}
```

---

#### create_symbol

Create a new symbol definition in a `.kicad_sym` library file. If the library doesn't exist, it's created. Duplicate symbol names are rejected.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `op_type` | string | Must be `"create_symbol"` |
| `target_file` | string | Relative path to `.kicad_sym` library file |
| `symbol_name` | string | Symbol name (1-128 chars) |

**Optional fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `reference_prefix` | string | `"U"` | Reference prefix (e.g. `"R"`, `"U"`, `"C"`) |
| `value` | string | `""` | Default symbol value |
| `pins` | array | `[]` | Pin definitions (max 200) |
| `properties` | array | `[]` | Additional custom properties (max 50) |
| `body_width` | number | `10.16` | Body rectangle width in mm (> 0, max 200) |
| `body_height` | number | `10.16` | Body rectangle height in mm (> 0, max 200) |

**Example:**

```json
{
  "root": {
    "op_type": "create_symbol",
    "target_file": "mylib.kicad_sym",
    "symbol_name": "OPAMP_DUAL",
    "reference_prefix": "U",
    "pins": [
      {"name": "OUT_A", "number": "1", "etype": "output"},
      {"name": "IN_A-", "number": "2", "etype": "input"},
      {"name": "IN_A+", "number": "3", "etype": "input"},
      {"name": "V-", "number": "4", "etype": "power_in"},
      {"name": "IN_B+", "number": "5", "etype": "input"},
      {"name": "IN_B-", "number": "6", "etype": "input"},
      {"name": "OUT_B", "number": "7", "etype": "output"},
      {"name": "V+", "number": "8", "etype": "power_in"}
    ]
  }
}
```

---

## Constraints

All operations must satisfy these constraints. Violations produce clear error messages from the Pydantic validator.

### target_file constraints

- Must be a **relative path** (no leading `/`)
- Must end in `.kicad_sch`, `.kicad_pcb`, `.kicad_sym`, or `.kicad_mod`
- No path traversal (`..` segments)
- No null bytes
- Length: 1-512 characters

### String length limits

| Field | Min | Max |
|-------|-----|-----|
| `reference` | 1 | 64 |
| `library_id` | 1 | 256 |
| `value` | 0 | 256 |
| `property_name` | 1 | 128 |
| `new_value` | 0 | 1024 |
| `net_name` | 0 | 64 |
| `bus_name` | 1 | 64 |
| `member_nets` items | 0 | 64 |
| `footprint_lib_id` | 1 | 256 |
| `prefix` / `prefix_filter` | 0 | 16 |

### Atomic operations

- One mutation per operation (no compound operations)
- One target file per operation
- Operations are wrapped in transactions with automatic rollback on failure

### Count limits

- `duplicate_component.count`: 1-100
- `array_replicate.count`: 1-100
- `add_bus.member_nets`: 1-32 items

---

## Workflow Guidance

### Before editing

1. **Read the target file first** to understand current state. Use `Read` to inspect the KiCad file and understand existing components, nets, and structure.
2. **Use exact reference designators** from the file. References are case-sensitive: `R1` is not the same as `r1`. Power symbols may use `#PWR01` format.
3. **Position coordinates are in millimeters** (mils are not supported).
4. **Check for unannotated components** (references ending in `?`) before operations that require specific designators.

### Constructing operations

1. Wrap the operation object in a `{"root": {...}}` envelope. The `root` key is required by the discriminated union schema.
2. Always include `op_type` as the discriminator field. It determines which operation model validates the rest of the payload.
3. Omit optional fields you do not need -- defaults will be applied.
4. For `position` / `spacing` objects, `x` and `y` are required. `angle` defaults to `0.0` if omitted.

### After editing

1. **Suggest running validation** if ERC/DRC is available for the target file type.
2. **Check round-trip fidelity** by reading the file back to confirm the change was serialized correctly.
3. **Report rollback status** if the operation failed -- the transaction system automatically reverts partial changes.

---

## Error Handling

### target_file validation fails

The error message includes the specific constraint violated:
- `"target_file contains null bytes"` -- null byte injection attempt
- `"target_file must be a relative path"` -- absolute path rejected
- `"target_file must not contain '..' path traversal"` -- path traversal rejected
- `"target_file must be a KiCad file type"` -- wrong extension

### Reference not found

If the specified reference does not exist in the target file, the error suggests listing existing components first. Use `Read` to inspect the file and find valid reference designators.

### Operation execution fails

If execution fails after validation passes, the error includes:
- A description of what went wrong
- A rollback confirmation indicating the file was restored to its pre-operation state
- The operation type and target file for audit traceability

### Net name validation

Net names and bus names reject whitespace-only strings. If a name is `"   "` (spaces only), the validator raises a clear error. Empty string `""` for `add_net.net_name` triggers auto-generation.

---

## Operation Quick Reference

| Operation | File Types | Required Fields |
|-----------|-----------|-----------------|
| `add_component` | sch, pcb | target_file, library_id, position |
| `remove_component` | sch, pcb | target_file, reference |
| `move_component` | sch, pcb | target_file, reference, position |
| `modify_property` | sch, pcb | target_file, reference, property_name, new_value |
| `duplicate_component` | sch, pcb | target_file, source_reference |
| `array_replicate` | sch, pcb | target_file, source_reference, pattern, spacing |
| `add_net` | pcb | target_file |
| `remove_net` | pcb | target_file, net_name |
| `rename_net` | pcb | target_file, old_name, new_name |
| `add_bus` | sch | target_file, bus_name, member_nets |
| `remove_bus` | sch | target_file, bus_name |
| `renumber_refs` | sch | target_file |
| `validate_refs` | sch | target_file |
| `annotate` | sch | target_file |
| `cross_ref_check` | sch | target_file |
| `assign_footprint` | sch | target_file, reference, footprint_lib_id |
| `swap_footprint` | pcb | target_file, reference, new_footprint_lib_id |
| `update_footprint_from_library` | pcb | target_file, reference |
| `validate_footprint` | all | target_file, footprint_lib_id |
| `verify_pin_map` | all | target_file, reference, footprint_lib_id |
| `add_wire` | sch | target_file, start_x, start_y, end_x, end_y |
| `add_label` | sch | target_file, name, position |
| `add_power` | sch | target_file, name, position |
| `add_no_connect` | sch | target_file, position |
| `add_junction` | sch | target_file, position |
| `add_lib_entry` | lib-table | target_file, lib_name, lib_type, uri |
| `remove_lib_entry` | lib-table | target_file, lib_name |
| `repair_schematic` | sch | target_file |
| `validate_power_nets` | sch | target_file |
| `add_copper_zone` | pcb | target_file, net_name |
| `set_board_outline` | pcb | target_file, width, height |
| `add_net_class` | dru | target_file, name, clearance, track_width, via_diameter, via_drill |
| `add_design_rule` | dru | target_file, name, constraint_type |
| `assign_net_class` | pcb | target_file, net_name, net_class_name |
| `auto_route` | pcb | target_file |
| `create_schematic` | sch | target_file |
| `create_pcb` | pcb | target_file |
| `create_project` | pro | target_file |
| `create_symbol` | sym | target_file, symbol_name |

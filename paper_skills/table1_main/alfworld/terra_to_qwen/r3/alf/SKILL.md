---
name: alf
description: "Embodied household-task skills distilled from execution experience."
---

## Core Approach


- When you spot an object that matches the task goal, take it immediately. If an item name matches the task object in the observation, use `take ...` before continuing any search.
- When the goal requires an object to be in a certain state (e.g., clean, cooled, sliced), apply that transformation immediately after picking up the object, before moving to the delivery location. Re‑read the goal after picking up the object; if a state is mentioned, navigate first to the relevant appliance (sink for clean, fridge for cool, microwave/toaster/stove for heated) and perform the state‑change action, then proceed to the final receptacle.


- **Every action** must appear verbatim in the current admissible actions list. Before acting, scan the list and select the action that exactly matches your intent. Never type a free‑form command.
- For placement tasks without a required state change, after taking the object, navigate directly to the target receptacle and use the `move` or `put` action. Do not examine or search further.

- **First action**: Your very first action must be a `go to` to a plausible location (e.g., countertop, table, fridge) based on the task goal. Never start with `look` or `inventory`; the initial observation already describes the room and you are not holding anything. Runtime check: before your first action, if you are considering `look` or `inventory`, stop and issue a `go to` to the most relevant container or exposed surface.
- **Perishable food priority**: If the task target is a food item that is typically refrigerated (e.g., tomato, fruit, vegetables, egg, milk), go directly to `fridge 1` as your first action. Do not search countertops, tables, or cabinets first. Runtime check: before your first navigation, ask: 'Is the target a perishable food item? If yes, go to the fridge.'
- **If the object is not in the fridge:** after checking the fridge and not finding the target, systematically search all exposed surfaces (countertops, tables, shelves) in ascending numerical order before opening any closed containers. Do not jump to a single guessed surface.


Maintain a strict subgoal order: acquire the target object, process it at the required appliance (if the goal specifies a state), then place it in the target receptacle. Before each action, verify it advances the current subgoal (obtain, process, or place). If not, reconsider.

- If the task involves using an object with a tool (e.g., `examine ... with desklamp`, `turn on ... with key`), after taking the object, navigate directly to the tool without examining the object. Only use `examine` or `look` on the object after the tool is active or in hand.


- **Compound task decomposition**: When the task instruction contains multiple verbs (e.g., "clean X and put it in Y"), decompose it into an ordered sequence of subgoals before acting. Execute each subgoal completely before moving to the next. **Runtime check:** after each movement, scan the admissible actions list for a new interaction verb that matches your current subgoal (e.g., `clean X with Y`, `move X to Y`) and execute it immediately before considering another move.
## Precondition Chains


- If the observation says a receptacle is "closed" (e.g., "The cabinet 1 is closed"), issue an `open` action on it before searching or interacting. Never leave a closed container without opening it first.
- When a task requires a state adjective (e.g., clean, cooled, heated), perform the transformation immediately after acquiring the object, before attempting to place it. Specifically, for cleaning, do not assume the object is already clean; verify and clean it at the nearest fixture. Runtime check: "Does my task contain a state word like clean or hot? If yes, did I perform that transformation on the object right after picking it up?"

- Do not assume an object already exists in the required state (e.g., a 'cool tomato' already in the fridge). Instead, locate any instance of the base object (e.g., 'tomato') and then apply the transformation. Runtime check: After picking up an object, if the goal adjective is not yet satisfied, ask: 'What appliance can I use to make this object [adjective]?'
- For cooling tasks specifically: after picking up the object, navigate to the fridge and use the action `cool <object> with fridge` (or the exact string shown in admissible actions) before moving to the target location.
  Do not clean the object before cooling; go directly to the fridge. **Runtime check:** Before using any `clean` action, verify that the goal explicitly contains "clean" or "wash"; if not, skip it.
- Use the `clean <object> with <fixture>` action explicitly; the fixture for cleaning is always a sinkbasin (e.g., `clean dishsponge 3 with sinkbasin 1`). After cleaning, verify that a `move <object> to <receptacle>` action appears in the admissible list before heading to the final location.

- For cleaning tasks specifically: after picking up the object, scan the admissible actions for a `clean <object> with <fixture>` command (e.g., `clean soapbar 2 with sinkbasin 1`) and execute it immediately. Do not assume the object is already clean based on its location; always clean it at the nearest basin before moving to the target receptacle.
## Search Strategy


- **Never revisit already-checked locations**: During a search phase, do not return to any receptacle (drawer, shelf, countertop, etc.) you have already inspected unless you have new information that the object may now be there. Before issuing a `go to` to a container, recall its last observed contents; if the target was not there, do not go. If you are about to `go to` a previously visited location, stop and select an unvisited one from the admissible actions. Runtime check: 'Have I already opened this container and seen its contents? If yes, and the target was not there, do not go.'

- **Target location first**: Before searching elsewhere, go to the receptacle mentioned in the task and check if the object is there. (Check: "Have I checked whether X is on Y?") If no receptacle is specified, navigate to the most plausible container (e.g., fridge for perishable food, countertops for small items) and search there first.
- **Exposed surfaces next**: Inspect every exposed surface (countertop, shelf, table) in order before opening any closed container. (Check: before opening a closed container, verify no unvisited exposed surface remains.)
- **Runtime check:** Before issuing an `open` action on a drawer, cabinet, or other closed container, ask: "Have I visited every exposed surface (table, countertop, shelf) in this room?" If not, navigate to the next unvisited exposed surface before opening any container.
- **Closed containers systematically**: Pick one container type (e.g., drawers, cabinets) and inspect all instances of that type in ascending numerical order.
 Complete all instances of the chosen type before moving to a different type (e.g., finish all cabinets before opening any drawers). Plan a fixed sequence. Before moving to a new container, check recent observations to confirm you have not already opened and checked it; if yes, skip to the next. Do not revisit already‑inspected receptacles. Exhaust all closed containers in the environment before returning to any location. (Check: "Have I opened all closed containers? Did I skip any instance?")
- **Open closed receptacles immediately upon arrival**: Before deciding whether a receptacle contains what you need, check if it is closed. If so, open it (use `open` action if available) and then examine its contents before leaving. Only leave once you have seen the container's contents.
  **Proven success**: This pattern has been shown to prevent errors; always open a closed container before attempting to examine or take from it.
- **Take visible targets immediately**: When the admissible actions list contains a `take <target> from <container>` action where `<target>` matches the goal object, execute it directly, even if you are not currently at that container. Do not navigate to the container first; the environment allows remote retrieval. If you are at a location and the observation lists the target object, issue a `take` command for that object before any other action at that location. Do not inspect or look around first. **Runtime check:** after arriving at a location, if the observation text explicitly mentions the target object (e.g., "you see a statue 1"), scan admissible actions for a `take <object> from <surface>` and execute it immediately; do not issue `look` or `examine`.

- **Avoid thematic guesses**: Do not go directly to a thematic object (e.g., toilet, sink, bed, bathtub) unless all general storage locations (cabinets, drawers, countertops, shelves) have been exhausted. **Runtime check:** after each unsuccessful inspection, ask "Which storage receptacle from the initial room description have I not yet visited?" and navigate to the next unvisited one.
- **Systematic surface scanning**: When searching across exposed surfaces (countertops, shelves, tables), visit each numbered instance in ascending order (countertop 1, countertop 2, …; shelf 1, shelf 2, …) until you have checked all of that type. If admissible actions contain a sequence of `go to shelf N` or `go to countertop N`, walk through each one before selecting any other destination. Before leaving a surface type, ask: “Have I visited every numbered instance of this type?” If not, go to the next unvisited number now. Only then move on to other open receptacles like basins or carts.
- **Surface checklist from initial observation**: At the start of a search in a room, identify all furniture items from the initial room description that could hold objects (e.g., coffeetable, sidetable, tvstand, sofa, bed, countertop, shelf, table, cart). Create a mental checklist and visit each one in a fixed order, marking each as checked. Do not revisit any checked surface until all candidates have been inspected. For surfaces with numbered instances (e.g., sidetable 1, sidetable 2), visit all instances in ascending order before moving to the next surface type. After arriving at a surface, the arrival observation already lists its contents; do not issue `look` or `inventory`. Instead, immediately issue a `go to` to the next unvisited surface in your checklist.
- **Exhaustive search runtime check:** Before navigating to a new container, ask: “Have I already opened every closed cabinet/drawer/shelf in my current surroundings? If not, which is the next unopened one in a fixed order?” Only proceed to a previously visited location after all closed containers have been opened.
- **No aimless revisiting**: During a search phase, never revisit a location you have already checked unless you have gained new information that gives a concrete reason to check it again. Before issuing `go to X`, ask: “Have I already been to X in this task phase? If yes, what new object or state change do I expect to find there?” If you cannot articulate a clear new expectation, go somewhere you have not yet visited.
- **Runtime check:** When facing a container described as 'closed,' look in the admissible actions for `open <container>` and execute it before attempting to examine or take from that container.
- **Use goal modifiers to infer starting location**: When the task goal contains a state modifier (e.g., "cool", "hot", "clean"), note the appliance you will need later, but do not navigate there first. Instead, start by searching exposed surfaces (countertops, tables, shelves) for the base object. Only go to the appliance after you have the object and need to apply the transformation. Runtime check: before your first navigation, identify the required appliance but go to a surface first.

- **Exception for perishable food**: If the target object is a food item commonly stored in a fridge (egg, milk, fruit, vegetables, etc.), the fridge is the most likely location to find it, even if the goal modifier suggests a different appliance. Navigate to the fridge first, pick up the object, then apply the transformation at the appropriate appliance. Runtime check: before your first navigation, ask: "Is the target a perishable food item? If yes, go to the fridge."

- **Holistic container scan**: Before committing to a single container type (e.g., dresser), list every container category visible in the initial observation (shelves, drawers, cabinets, dressers, etc.). Plan to visit each category in turn, checking all instances of that type before moving to the next. Do not linger on one category if the target hasn’t been found; move to the next unvisited category. Runtime check: after checking all instances of one category, ask “Which container category have I not yet visited?” and navigate to the next one.
- **Closed‑container runtime check**: When you arrive at a container and the observation describes it as closed (e.g., “The drawer 1 is closed”), immediately use the `open` action before examining the container or moving to another location. Do not skip a closed container that could plausibly hold the target.
- **After checking a closed container**: Before opening another closed container, confirm that all exposed surfaces (countertops, tables, shelves) have been inspected. Runtime check: "Have I visited every countertop, table, and shelf mentioned in the room description?" If not, visit the next unvisited exposed surface.
- **Start-of-task surface priority**: At the very beginning, before opening any closed container, navigate to an exposed surface (e.g., countertop, diningtable, shelf) that appears in admissible actions. Check the object list there before moving to any closed receptacle. **Runtime check:** Before your first navigation action, verify that you are going to an open surface (countertop, table, shelf) and not a drawer or cabinet. If the admissible actions list contains an open surface, you must go there first.

- **Exception**: if the target is a perishable food item (fruit, vegetables, dairy, eggs, etc.), navigate directly to the fridge, ignoring open surfaces.
- **Infer from associated tools**: When the task mentions a tool or fixture (e.g., desklamp, lamp, flashlight), assume the target object is located on the surface where that tool is typically found (e.g., desk for desklamp, nightstand for lamp). Navigate to that surface first. Runtime check: after reading the task, if a tool is mentioned, identify its typical location and go there before any other action.

- **Surface-typical objects first**: For objects that are normally found on furniture surfaces (e.g., lamps, clocks, books, radios, remote controls), restrict your search to the exposed surfaces listed in the initial room description (desks, dressers, tables, shelves, nightstands) before opening any drawers, cabinets, or other closed containers. Only after every plausible surface has been checked and the object is still missing, consider containers. Runtime check: "Is the target object typically found on top of furniture? If yes, have I checked every furniture surface in this room?"

- **Open surfaces first**: Before opening any closed container (cabinet, drawer, dresser, etc.), visit every open surface (countertop, shelf, table, sidetable, coffeetable, tvstand, etc.) in the room in ascending numerical order. Moving to an open surface immediately reveals its contents, saving the extra step of opening. **Runtime check:** before issuing `go to cabinet X` or `open cabinet X`, ask: "Have I visited every open surface (countertop, shelf, table, sidetable, coffeetable, tvstand) with a visible ID in this room?" If not, navigate to the next unvisited open surface. Additionally, before opening any closed container, confirm all open surfaces have been visited: ask "Have I visited every open surface in this room?" If no, do not open the container; go to an unvisited open surface first.

- **Infer typical surface for object type**: When the task mentions an object, identify the furniture piece that typically holds that object type (e.g., desk for alarmclock, dresser for lamp, shelf for small items) and navigate there first, before searching elsewhere.

- **Never leave a closed container unopened**: When you arrive at a container and the observation says it is closed (cabinet, drawer, microwave, etc.), you must open it before moving away. Even if you suspect it’s empty, the only way to be sure is to open it. Runtime check: before issuing any `go to` away from a container, ask “Is this container closed? If yes, did I open it?” Only leave after it is open and you have seen its contents.
- **After opening a container:** If the target object appears in the observation (the container's contents), use the `take` action immediately. Do not leave the container without retrieving the target.
- **Strict no‑revisit rule during search**: While searching for the target object, never return to a location you have already inspected. If you catch yourself about to `go to` a previously visited container or surface, stop and instead navigate to the next unvisited container in your fixed order (e.g., cabinets 1‑10, then drawers 1‑3). Revisiting wastes steps and guarantees you will miss unsearched containers. Runtime check: before each `go to` action, confirm the destination is not already in your mental “visited” list.
- **Runtime check:** When you need to inspect a container, use `go to <container>`; the arrival observation will list its contents. Do not use `look` to inspect a container from a distance.
- **Skip non‑target items during container scans**: When searching a series of closed containers (e.g., drawers, cabinets), after opening one and seeing its contents, if the target object is not listed, immediately `go to` the next container in the sequence without issuing any `take` actions. **Runtime check:** after opening a container, if the target object name does not appear in the observation, skip all `take` actions and navigate to the next unopened container in your planned order.

- **Dishware**: Plates, cups, bowls, and similar items are almost always found on countertops, diningtables, or kitchen islands. Check those surfaces before opening any cabinets.

- **Cookware on stoveburners**: When the target object is a pot, pan, or other cookware, inspect every stoveburner in the room before opening any cabinets, drawers, or shelves. Use `go to stoveburner N` for each numbered burner in ascending order. Only after all burners have been checked and the object is not found, move to storage furniture.
## Action Validity & Recovery


- **Skip redundant observations**: Avoid `look`, `examine`, or `inventory` when the current observation already provides the needed information. Do not use `look` immediately after moving to a new object or container; the arrival observation already describes what is there. Reserve `look` for re‑orienting if you are lost, or after an action that might have changed the surroundings. Use `inventory` only to confirm what you are holding before using an item. Before issuing any observation action, ask: "Does this action give me information that is not already clear from the current observation?" If not, skip it. (Runtime: When about to emit `look`, ask: "Did I just arrive at this location and already see its contents in the last observation? If yes, skip `look`.")
- **Always select actions from the admissible actions list** shown after the observation. Before emitting an `<action>`, verify that the exact string appears verbatim in the current admissible list.

- **Prioritize task‑advancing actions**: Before any action, scan the admissible list for commands that directly complete your current subgoal (e.g., `clean … with …`, `put … in …`, `move … to …`, `use …`). If one exists, execute it immediately without inserting `look`, `examine`, or other non-essential actions. *Runtime check:* Before each action, ask: 'Does this action directly advance the current subgoal? If not, is there an admissible action that does?' If a task-advancing action is available, select it right away.

- **Direct goal action after gathering objects**: When you have all required objects at the same location and the task goal is a specific interaction (e.g., "look at X under the desklamp" implies turning on the lamp), scan admissible actions for the action that directly achieves the goal (e.g., `use desklamp 1`). Execute it immediately without any `examine`, `look`, or `inventory` actions. Runtime check: "Am I at the location with all objects needed? If yes, what one action completes the task? Execute it now."

- **Keep reasoning concise.** If you find yourself deliberating for more than a few sentences, stop and select the first admissible action that directly advances the goal. Overthinking wastes steps and rarely improves decisions.

If the action you need (e.g., `put`, `move`, `clean`) is not in the admissible list, pick an available action such as `examine <target>` or `inventory` to help the environment surface new admissible actions. Never invent actions.
- **Light source activation**: If the task mentions a lamp or desklamp, activate it with `use <light>` as soon as you reach its location, before examining the target object. Runtime check: "Does the task mention a lamp or other light? Is it on yet?"
## Task-Type Procedures



### Placement Tasks
When the goal is to move an object to a target receptacle: after picking up the object, navigate directly to the target location and use the `move X to Y` action. Avoid examining other objects or locations.

- **Open destination first**: Before searching for the object, navigate to the destination receptacle and open it if it is a closed container. This prepares the destination so you can place the object immediately after any required transformations.
- **Apply required transformations before moving**: If the task goal includes a state adjective (e.g., cool, hot, clean, sliced), perform the corresponding transformation action at the appropriate appliance immediately after picking up the object, before navigating to the target receptacle. Use composite actions (e.g., `cool X with fridge`, `heat X with microwave`) directly without opening or examining the appliance. **Runtime check:** Before issuing any `move` or `go to` to the target, re-read the task; if an adjective is present, confirm that you have executed the transformation action and seen a success message. If not, go to the appropriate appliance and perform it now.
- **Runtime check:** after a successful `take` action, if the target receptacle is visible in the current observation, navigate to it with `go to <target receptacle>` and then `move <object> to <target receptacle>`. If the target receptacle is not visible, start searching for it using the systematic search strategy (treat the receptacle as the search target).
- **Heating tasks**: After picking up the object, heat it with the microwave (or toaster/stove) before moving to the target location. Once at the target, check admissible actions for a `move X to Y` entry; if present, use it directly. Do not use `put` or `place`.

  **Important**: Even if you found the object inside the microwave, it is not yet heated. You must still execute the `heat X with Y` action explicitly before moving to the target.
**Runtime check at appliance**: When you arrive at the microwave (or stove/toaster) holding the object, scan the admissible actions for a composite action like `heat X with Y`. If present, execute it directly; do not open the appliance, move the object inside, or close it.
- **Runtime check:** before issuing `move X to Y`, confirm that the observation starts with "You arrive at" (indicating you are at the target receptacle) and that the `move` action appears in the admissible actions list.

- **Do not use transformation actions for placement**: When the task goal is to put an object in a receptacle, use `move X to Y` directly. Do not use `cool`, `heat`, `clean`, or similar composite actions unless the goal explicitly requires that transformation. Runtime check: before using `cool X with Y`, verify that the task goal contains a word like 'cool' or 'chill'. If not, use `move`.
- **Runtime check:** While holding the target object, scan admissible actions for a `move` action to the target receptacle. If found, execute it immediately without any intervening actions.
- **Runtime check before placing:** If a `move X to Y` or `put X in Y` action appears in the admissible actions list, execute it immediately; do not manually open the target receptacle first, even if the observation says it is closed. The environment handles any necessary opening.
- **Sequential delivery for multiple objects**: If the task requires moving multiple objects to the same or different receptacles, deliver each object completely before picking up the next. Never attempt to take a second object while still holding one. After picking up an object, go directly to its destination and place it with `move X to Y`; only then return for the next object. **Runtime check:** before issuing any `take` action, verify your inventory is empty. If you are holding something, first deliver it to its destination before picking up another item.

- **Runtime check after pickup for multi-object tasks:** After a `take` action that successfully places an object in your inventory, if the task goal requires delivering multiple objects and your inventory was empty before the take, immediately navigate to the destination (`go to <destination>`) and use `move <object> to <destination>` to deliver the held item before returning for the next one.


- **Direct delivery after pickup**: Once you have the target object, go straight to the delivery receptacle and use `move` to place it. Do not inspect other locations or perform unnecessary actions. Runtime check: after a successful `take`, verify that your next two actions follow the pattern: `go to <destination>` then `move <object> to <destination>`. Confirm that both actions appear in the admissible list and execute them in sequence to finish the task.

### Instrument Tasks
- For tasks requiring an instrument (e.g., desklamp, lamp) to examine or interact with an object: If the task is phrased "look at X under the Y" or "examine X with the Y", identify the location that typically hosts both the target object and the instrument (e.g., desk for alarmclock and desklamp). Navigate there as your first action. If the object is not at that location, go to its likely location first, take it, then go to the instrument.
- Upon arrival at the instrument location with the object (or if the object is there), take it if not already held.
- Immediately use the instrument (e.g., `use desklamp 1`) without examining the object, looking around, or moving the object elsewhere.
- **Runtime check:** Before your first action, confirm that you are moving toward the location hosting both the target object and the instrument. If the object and instrument are not co-located, go to the object's likely location first, then to the instrument. After taking the object, scan admissible actions for `use <instrument>` and execute it immediately; do not insert any `examine`, `look`, or `move` actions.
## Common Pitfalls


### Redundant Observations and Inventory Checks
- Do **not** use `look` just to reconfirm a room you have already described; only use `look` when you suspect the environment has changed or lack a recent object list.
- Do **not** re‑open `inventory` unless you need to verify whether you already picked up an object before moving it. Remember what you are carrying from previous observations.
- **Runtime check:** Before typing `look` or `inventory`, ask: "Did I already receive a full object list (initial observation or arrival description)?" and "Do I already know what I’m carrying from a previous observation?" If yes, skip the action.

After a `go to` command, the resulting observation is the arrival observation and already lists the objects present (e.g., "On the countertop 1, you see a soapbar 2"). Do **not** use `look` immediately after arriving. **Runtime check:** "Did I just move to a new location? If yes, the current observation already describes what's there. Skip `look`."
- **Admissible-action check before `look`:** Before issuing `look`, scan the admissible actions list. If it contains a concrete action that directly advances your current goal (e.g., `take X from Y`, `move X to Z`, `go to <destination>`), select that action instead. Reserve `look` for when the observation does not yet list the objects you need to interact with.
- **CRITICAL: At task start, skip `look`** — the initial observation already describes the room and you are not holding anything. Go directly to a plausible surface (countertop, table, shelf). Only check inventory after you have picked up an object and need to confirm you are holding it.

- **At task start, skip `look`**: the initial observation already describes the room and lists containers. Do not use `look` as your first action. Instead, navigate directly to a container that is a plausible location for the target object (e.g., a countertop for food items).
- **During search, skip inventory after confirmation**: Once you have confirmed you are not carrying the target object, do not re‑check inventory until you have successfully picked up an object. Only use inventory to confirm what you are holding after a take action.

- **When you arrive at a closed container, do not check inventory or use `look`; open the container immediately.** The arrival observation already tells you the container is closed, and opening it is the only way to see its contents.

- After taking an object from a container, do not re‑examine that container. The contents are unchanged. Proceed directly to delivering the object. Runtime check: after a `take` action, if `examine <container>` appears but no further `take … from <container>` is listed, skip the examine and go to the delivery location.

- When the task goal mentions an instrument (e.g., "examine ... with the desklamp"), do not examine or inspect the target object until you are at the instrument's location and the instrument is usable. First, locate and pick up the target object (it may not be at the instrument location; if not, go to where it is likely to be, e.g., bed for pillow, desk for clock). Then navigate directly to the instrument and apply it. **Runtime check:** before using `examine` or `look` on an object, ask: "Does the task require an instrument that I haven't yet reached?" If yes, delay the examination until you are at that instrument. Before going to the instrument, ask: "Is the target object already at the instrument location? If not, where is it likely to be?" Go there first and pick it up.
- **After picking up the target object, if the instrument is not visible at the current location** (no `use` or `turn on` action in the admissible list), navigate to another plausible surface (e.g., shelf, desk) to find it before examining. Runtime check: after a `take` action that secures the target object, scan admissible actions for tool‑related verbs. If none are present, go to a location where the instrument is likely to appear.

- When you arrive at a container and the observation text explicitly lists its contents (e.g., "On the desk 1, you see …"), do not use `look` or `examine` on that container. If the observation contains a sentence starting with "On the …", "In the …", or similar explicit listing, you already have the needed information; skip `look`/`examine` and directly interact with a listed object.
- After picking up an object, do not examine it or open inventory unless the task goal explicitly requires verifying a property of the object (e.g., "examine the cd under the lamp"). Instead, proceed directly to the next step (delivery or searching for the next required item).

- **After completing a transformation action** (e.g., clean, heat, cool), do not use `look` or `inventory`. Navigate directly to the next known destination. Runtime check: after every action that completes a subtask, ask 'Do I already know exactly where to go next?' If yes, go there immediately without any intermediate look or inventory step.

- **After a successful `take` action**, do not use `look` or `inventory`. The current observation already describes your surroundings. Instead, immediately navigate to the next required location (appliance for transformation, or destination receptacle) using `go to` and then the appropriate action.
### Adjacent‑Container Interactions
- When standing at a container (e.g., drawer 3), scan the admissible‑action list for interactions like `open drawer N` or `examine drawer N` where `N` refers to a **different but nearby** container.
- Execute that action directly without an extra `go to` movement.
- **Runtime check:** Before issuing `go to drawer X`, look through admissible actions for strings like `open drawer Y` or `examine drawer Y` where `Y` is not your current location. If one exists, use it instead.

### Picking up irrelevant objects
- Before any `take` action, confirm the object's name exactly matches one of the target objects listed in the task instruction. Ignore non‑target items unless they are explicitly required as tools (e.g., a key to unlock a container).

Before picking up an object, ask yourself: "Does this item's name contain the exact noun from the task?" Do not accept near-matches (e.g., "pot" for "pan", "soap" for "soapbar"); the object name must contain the exact noun from the task.


- **Runtime check:** Before executing a `take` action, verify that the object's full name in the admissible action (e.g., `take pencil 3 from shelf 1`) contains the target object word (case‑insensitive). If it does not, do not take it; continue searching. For example, "pen" is not "pencil"; "mug" is not "cup".
### Skipping Required Transformations
- After picking up an object, re-read the task instruction and list every transformation verb (heat, clean, slice, cool, etc.). Check your recent action history for a confirmation that each transformation was performed on the object (e.g., "You heat the plate 3 using the microwave 1"). If any transformation is missing, perform it immediately before moving to the delivery location.
- Runtime check: before issuing a `move X to Y` or `put X in Y` action, scan the last 5 observations for a confirmation message containing the target verb. If not found, return to the appliance and use the composite action (e.g., `heat X with Y`).

### Manual Appliance Manipulation Instead of Composite Actions
- When you need to use an appliance (microwave, stove, toaster, fridge), first check if it is closed (observation says "is closed"). If so, open it (e.g., `open fridge 1`). Then scan the admissible actions for a composite action (e.g., `heat X with Y`, `cool X with Y`). Use that action directly; do not manually close or reopen the appliance after the transformation unless the task requires it.
- Runtime check: before using an appliance, if it is closed, open it first. Then look for the composite action; if found, use it instead of any manual open/close.
- **Concrete example**: If you need to cool an apple and are at the fridge, and the fridge is closed, first `open fridge 1`. Then use `cool apple 1 with fridge 1`. Do not close the fridge after cooling unless needed.

- **If the object is already inside the appliance** (e.g., tomato in microwave), do not open the appliance to take it out. Use the composite `heat X with Y` action directly; it works regardless of whether the object is inside or in your inventory.
### Unnecessary Appliance Closing
- After heating, cooling, or cleaning an object, do not close the appliance unless the task explicitly requires it or you are blocked from moving. Move directly to the next step.
- Runtime check: Before issuing a `close` action on an appliance, verify that the task goal or the admissible action list requires it for the next step. If not, skip it.


### Location-Shuttling Loops
- If you leave a location empty‑handed and return later without having acquired or used any new object, you are trapped in a loop. Before leaving, ask: "What object, if taken now, would change the situation at my destination?" Take that object, or stay and search until you identify what you are missing.
- **Runtime check:** after each `go to`, if you have visited this location before in the same task phase and have not acquired any new object since the last visit, do not go there again. Instead, stay at your current location and search for the missing object, or go to a location you have not yet visited that could contain it.
## New Section

### Misidentifying Objects
- Do not assume an object is the target under a different name. Treat object names literally.
- **Runtime check:** Before picking up or interacting with a substitute object, stop and ask: “Is the object mentioned in the goal actually present under its own name in the observation? If not, have I searched elsewhere for it?”
---
name: alf
description: "Embodied household-task skills distilled from execution experience."
---

## Core Approach


Parse the task instruction to identify the key target and context objects before acting.

**Immediate Target Acquisition**: When the task names a specific movable object (e.g., "cd", "apple", "knife"), infer its likely location from the task context or initial observation and navigate there as your first action. Upon arrival, take it immediately. Do not search other locations or examine surroundings first—secure the known target object without delay. Before each action, self-check: "Is this next action directly related to one of the objects named in my task goal?" Prioritize navigation and interactions that involve those specific objects. Ignore irrelevant objects in the environment.
If the task is to put X in/on Y, then Y is the target location. Your first action must be to navigate to Y and examine its contents. Only if X is not there, proceed to search other locations.
When the task names a landmark object (e.g., desklamp, alarmclock), infer its likely surface (desk, sidetable) from the initial room observation and navigate there as your very first action. Do not search other containers before visiting the landmark's surface.

Before any task-critical interaction, locate every distinct object named in the task instruction. When the goal says to use object A "with" object B, do not repeatedly interact with A alone—search unexplored surfaces systematically until B is found, then bring them together or activate B before the final action.

Runtime check: list all objects from the task instruction. For each, confirm: "Have I seen this object or is it in my inventory?" If any object is still unseen, the next action must be to go to an unexplored surface or container, not to interact with objects already held.

When a task names a target object, infer its likely location from semantic associations (e.g., bowls → desk/table/shelf, lamps → desk/sidetable). Navigate to the most semantically associated surface first before exploring unrelated receptacles.

Decompose every task into ordered sub-goals before acting: (1) acquire the target object, (2) perform any required transformation (cool, heat, slice, etc.) at the appropriate appliance, (3) place the transformed object into the goal receptacle. State the sub-goal chain explicitly and ensure each action advances toward the next unmet sub-goal.

Prefer direct admissible actions over multi-step setups. When a subgoal matches an action in the admissible list (e.g., `heat`, `cook`, `cool`), execute it immediately. Do not pre-open appliances unless the action fails without it.

Before placing an object into its target receptacle, scan the goal for adjectives (clean, hot, cooled, sliced, etc.). If any adjective implies a state change, perform the transformation at the appropriate appliance before heading to the final destination. Runtime check: when holding the target object, ask "Does the goal require a transformation I haven't performed yet?" If yes, go to the appliance first.

### CRITICAL: Before Opening Any Closed Container

### CRITICAL: Search Priority Order
Follow this exact priority for every search:
1. **Target location first**: If the task names a destination receptacle/surface, go there first to check if the object is already present.
2. **All destination-type instances**: If placing into a type (e.g., stoveburner), visit every instance of that type.
3. **Every open surface**: Countertops, tables, shelves, desks, sidetables, beds, garbagecans, stoveburners — check them all before any closed container.
4. **Closed containers last**: Drawers, cabinets, fridges — in sequential numeric order, one container type at a time. **WARNING: Never open a drawer or cabinet before all open surfaces have been visited.**

**Revisit Blocker (MANDATORY)**: Maintain a written CHECKED list: "CHECKED: [location] — no [target]." Before every `go to X` or `open X`, scan the list. If X is on it, skip it. Never revisit unless you placed something there. Failure example: agent revisited fridge 9 times and cabinet 1 four times despite already confirming they were empty. This rule is especially critical for drawers and cabinets: once you have opened a drawer or cabinet and found it empty, add it to your CHECKED list and never return to it unless you later place the target object there.

**Category-by-Category Sweep**: Group admissible `go to` targets by type. Complete one full group before moving to the next. After every 5 moves, confirm which groups remain unvisited.

**Runtime Check Before Opening Closed Container:** Before selecting any `go to <closed container>` or `open <closed container>` action, scan the admissible `go to` list for any open surface location (countertop, table, shelf, stoveburner, etc.) that you have not yet visited. If any such unvisited open surface appears, navigate there first. Only when every open surface from the initial observation has been visited may you open a closed container. After any closed container check fails to find the target, immediately return to step 3 and exhaust all remaining unvisited open surfaces before opening another closed container. Runtime check: after a closed container fails, ask "Are there any open surfaces from the initial observation I haven't visited?" If yes, go there next.

**Concrete Example**: "put toiletpaper on toiletpaperhanger" → first action: `go to toiletpaperhanger 1`. If not there, sweep all open surfaces, then cabinets/drawers.
### CRITICAL: Search Priority Order
Follow this exact priority order for every search. Do not skip ahead:
1. **Every open surface first**: Visit every countertop, table, shelf, desk, sidetable, bed, garbagecan, toiletpaperhanger listed in the initial observation. This applies even when the target object seems like it "should" be in a container — check surfaces first. If the goal involves placing an object into a target location, include that target location in your open-surface sweep.
2. **Closed containers last**: Only after step 1 is fully exhausted, open drawers, cabinets, and other closed storage in sequential order.

**Open Surface Check Before Closed Container**: Before choosing `go to` any closed container (drawer, cabinet, fridge, etc.), scan the initial room observation for surfaces (countertops, tables, shelves, diningtables, desks, sidetables, beds, garbagecans). If any such surface remains unvisited, go there first. Runtime check: "Was there a surface mentioned in the initial observation that I haven't inspected yet?" If yes, navigate to that surface before opening a closed container.

**Revisit Blocker**: Maintain an explicit written list of every location you have visited and confirmed does NOT contain the target. After each inspection, add it to the list: "CHECKED: [location name] — no [target]." Before every "go to X" or "open X" action, scan your CHECKED list. If the destination is already on the CHECKED list, skip it and choose an unvisited location. Never revisit a location unless you have taken an action that would change its contents (e.g., placing an object there).

Example failures: Agent went to drawer 1 without checking countertop or toiletpaperhanger — toilet paper was on countertop 1. Agent revisited fridge 4 times and cabinet 1 twice despite already confirming they lacked bread. Correct: check open surfaces first (countertop 1, toiletpaperhanger 1), then drawers, tracking every checked location and never revisiting without cause.


**Concrete Example**: For a task like "put toiletpaper on toiletpaperhanger", your first action must be `go to toiletpaperhanger 1`. Do not go to cabinet 1 or any other closed container before checking the target location. If the object is not at the target, then exhaust all open surfaces (countertops, tables) before opening any cabinets or drawers. This directly applies the Search Priority Order: target → open surfaces → closed containers.
**Category-by-Category Sweep**: Before starting a search, mentally group all admissible `go to` targets by type (countertops, stoveburners, cabinets, drawers, appliances). Visit one full group at a time. Track which groups you have already checked and do not revisit a group unless new information justifies it. Runtime check: after every 5 move actions, list which object-type groups you have visited and whether any unvisited group remains. If so, proceed to the next unvisited group.
### Landmark-First Search (Critical)
When a goal mentions a prepositional landmark (e.g., "under the desklamp", "on the desk"), locate that landmark BEFORE handling any target object. If the landmark is not visible in the current observation, visit every unexplored surface and location in the admissible action list systematically until the observation explicitly shows the landmark. Do not assume the landmark is on the same surface as the target object.

**Anti-Loop Rule**: Never return to the target object's origin location more than once. After picking up the object, if the landmark is absent, immediately begin a systematic sweep of all unexplored locations (shelves, desks, tables, etc.). Do not re-examine, re-place, or re-handle the object at its origin—this is a fixation loop. Runtime check: before any action after picking up the object, ask "Am I about to interact with a location I've already visited?" If yes, redirect to the next unexplored location.

**Fixture-Action Scan**: At every new location, scan the admissible actions for any "use <landmark>" or "turn on <landmark>" action. If one appears, select it immediately—do not continue exploring. Runtime check: after arriving at each location, ask "Does the admissible action list contain a 'use' or 'turn on' action for the goal fixture?" If yes, execute it without delay.

Runtime check: before adding any navigation step, ask "Does this action directly serve locating the target object or the required tool?" If not, skip it and stay on the direct path from object to tool to goal.


**Systematic Surface Sweep After First Miss**: If the landmark is NOT found on the first expected surface, immediately visit EVERY other surface listed in the initial room observation (shelf, sidetable, dresser, etc.) before re-examining or re-handling the target object. Do not return to the first surface until all others are checked. Runtime check: after the first miss, ask "Have I visited every other surface from 'Looking quickly around you'?" If not, go to the next unvisited surface.
**Activate Landmark Immediately**: When you locate the landmark device (lamp, etc.), activate it ON THE SPOT before fetching or handling the target object. Do not leave the landmark's location to retrieve the target object first. The correct sequence is: locate landmark → activate landmark → then bring the target object to the activated landmark. Runtime check: upon seeing the landmark, scan admissible actions for "use <landmark>" or "turn on <landmark>" and execute it immediately — do not navigate away.
## Precondition Chains

## Search Strategy


### Surface-First Checkpoint (Prevent Drawer Fixation)
Before opening any drawer, cabinet, or closed container, confirm you have visited EVERY visible surface receptacle listed in the initial observation (coffeetables, sidetables, desks, shelves, countertops, diningtables, beds). Statues, mugs, phones, and other small displayable objects are far more likely on open surfaces than inside drawers. Runtime check: "Have I visited all surface-type locations before my first 'open drawer/cabinet' action?" If any surface remains unvisited, go there next.

### Open Surfaces First (CRITICAL)
At the start of any search task, visit every countertop, table, shelf, and open surface listed in the initial observation before opening any closed container. If an observation says "you see a [object]" without saying "closed," inspect it immediately. Only after exhausting all open surfaces should you move on to cabinets, drawers, and other closed storage. Runtime check: before your first "open <container>" or "go to <closed-container>" action, scan the admissible action list for "take" actions involving visible surfaces. If any surface remains unvisited, go there next — the target object is often sitting in the open (e.g., spoons on diningtables, toiletpaper on countertops).

### Never Revisit Exhausted Locations
Maintain a written CHECKED list of locations you have already confirmed do not hold the target. Before navigating to or opening a receptacle, scan your CHECKED list. If the location is on it, skip it and proceed to the next unvisited location. Runtime check: before each "go to X" or "open X" action, ask "Is X on my CHECKED list?" If yes, choose an unvisited destination instead.

### Target-First Search
When the task goal involves placing an object into a target location (receptacle or surface like desk, shelf, table), go to that location FIRST to check whether the object is already there. Do not search other locations before checking the target. This is especially important when the target location semantically matches the object type (e.g., fridge for perishable food, microwave for heatable items) — the object is often already there. Runtime check: before moving away from the starting position, ask "Have I already visited the target container or surface?" — if not, go there first.

If the target object is NOT at the destination, immediately pivot to the nearest closed storage (drawer, cabinet, fridge) that could reasonably hold it. Do not exhaustively check every open surface before moving to containers. Runtime check: after arriving at a location, if visible objects are listed but the target is absent, your next action must be a "go to" a storage container, not another open surface.

### Semantic First-Target
After reading the task, identify the primary object's most likely surface or container. Make your first "go to" action target that surface. Only fall back to exhaustive exploration if the inferred location yields nothing.

Concrete examples: perishable food (tomato, lettuce, apple, bread) → go to fridge first. Dishes/plates → cabinets. Utensils (knife, fork, spoon) → drawers. Lamps → desks/sidetables. Only after exhausting the semantically most-likely location should you fall back to broader search. Runtime check: before your first navigation action, ask "What receptacle type commonly contains [target object]?" and prioritize that type (e.g., fridge for fruit, countertop for dishes).
### Systematic Category Search
Search locations systematically by category: start with drawers, then sidetables, then other surfaces. Visit each distinct location type before moving on. Always select actions from the provided admissible actions list only.


### Open Surface Exhaustion Check
Before emitting any `open <container>` action, run this check: list every open surface from the initial room observation (countertops, tables, shelves, desks, sidetables, beds, garbagecans). Confirm you have visited each one and read its contents. If any open surface remains unvisited, go there next. Do NOT open a drawer, cabinet, or closed container until every open surface is exhausted.

### Revisit Blocker
Maintain an explicit written list of every location you have visited and confirmed does NOT contain the target. After each inspection, add it to the list: "CHECKED: [location name] — no [target]." Before every "go to X" or "open X" action, scan your CHECKED list. If the destination is already on the CHECKED list, skip it and choose an unvisited location. Never revisit a location unless you have taken an action that would change its contents (e.g., placing an object there).

### Sequential Container Search
When searching a series of like containers (e.g., cabinet 1 through cabinet 13), inspect them in logical order (numeric or alphabetic). Open one, note its contents, then move to the next adjacent container. Do not skip to a non-adjacent container unless you have a specific reason to believe the target is there. This prevents missed locations and eliminates the need to later backtrack.

### Open Every Closed Container in Sequence
When searching a room, progress through ALL containers in a fixed numbered order (e.g., drawer 1 → drawer 2 → drawer 3 → drawer 4 → drawer 5 → drawer 6). For each container: if closed, open it. If open, inspect its contents. Never skip a closed container to revisit an already-opened empty one. At runtime, ask: "Is this container closed? If yes, open it. Have I checked every container in the sequence? If not, continue to the next unopened one."

### Fixed Spatial Search Route
Before searching, define a fixed route through all locations in the room (e.g., "shelf 1 → shelf 2 → drawer 1 → drawer 2 → drawer 3 → drawer 4 → drawer 5 → drawer 6 → desk 1"). Follow this route in order without deviation. Complete the entire sequence before starting over. Do not jump to a high-numbered drawer before checking lower-numbered ones. At runtime, check: "Am I following my fixed search sequence? Have I completed the current sequence before making an arbitrary jump?"

### Multiples: Containers First
When the task requires two or more of an object type (e.g., "two saltshakers"), prioritize closed storage (cabinets, drawers, fridges) over open surfaces. Small multiples often live together in containers. Only fall back to open-surface search if all containers are exhausted without finding enough copies.

### Grab on Sight
At each new location, immediately scan the admissible actions for any "take <target_object> from <location>" entry. If present, take the object now. Do not note it and return later—deferring pickups causes costly revisits. Example: if you arrive at diningtable 1 and see "take lettuce 1 from diningtable 1" in the admissible list, execute it immediately. Do not leave the lettuce there while you search other cabinets.

When multiple instances of the required object type are visible (e.g., spoon 3 and spoon 4), immediately take the first one listed in the admissible actions. Do not deliberate or search elsewhere.

Before taking, verify that the object's name exactly matches the target object from the task description. If the object is similar but not identical (e.g., 'pot' when you need 'pan'), leave it and move on.


### Small Objects: Open Surfaces First
Small portable objects (knives, forks, apples, phones, keys, pens) are far more likely to rest on countertops, tables, and open shelves than inside closed storage. When searching for any small object, inspect EVERY open surface in the room before opening a single cabinet, drawer, or closed container. Check: before your first `open` or `go to cabinet/drawer` action, have you visited and observed every countertop/table/shelf surface listed in the initial room description?

### Post-Container Surface Check
After opening any closed container and confirming the target object is not inside, pause before opening the next container. Review the current admissible "go to" list for any unvisited surface-type locations (countertops, diningtables, shelves, desks). If any surface remains unvisited, go there next. Do not open a second closed container until every reachable surface has been checked.

### Destination-First Sweep & Type-Sweep Order
When the task requires placing an object into a specific receptacle type (e.g., stoveburner, shelf, drawer), visit EVERY instance of that receptacle type before opening any storage containers. Example: if the goal is "put X on a stoveburner," go to stoveburner 1, stoveburner 2, stoveburner 3, etc., checking each for the target object. Only after exhausting all instances of the target receptacle type should you search cabinets, drawers, or other storage. Additionally, complete a full sweep of one location type (all stoveburners, then all countertops, then all drawers, etc.) before moving to the next type. Do not return to any location of an already-swept type until every other type has been checked at least once. Runtime check: after reading the task, identify the destination receptacle type and ask "Have I visited every instance of this receptacle type?" If not, do that before any storage-search action.

When visiting the destination receptacle early in the episode, open it immediately if it is closed. This prepares the receptacle for the final placement step and saves a step later. Runtime check: after arriving at the destination, if the observation says it is closed, open it before leaving to search for the target object.
### Exhaust All Container Types Before Re-Searching
Before starting a search, scan the admissible actions list and enumerate every distinct container type present (e.g., shelves, drawers, dressers, garbagecans). Visit ALL types—not just the most obvious ones—in a fixed order. Do not skip a type because it seems unlikely; small objects often end up in unexpected receptacles. Only after every type has been exhausted should you consider re-searching a previously visited type.

### Exhaust Half Before Switching Container Types
When searching a numbered series of containers (e.g., drawers 1–6), open at least half of the available instances before abandoning that type for another. Count how many you have opened; if fewer than half remain unchecked, continue with the current type. Use the admissible-actions list to verify unexplored numbered instances remain. This prevents premature switching that leads to wasteful re-searching of already-exhausted locations.


### Target-First Search
When the task goal involves placing an object into a target location (receptacle or surface like desk, shelf, table, toiletpaperhanger), go to that location FIRST to check whether the object is already there. Do not search other locations before checking the target. Runtime check: before moving away from the starting position, ask "Have I already visited the target container or surface?" — if not, go there first.

If the target object is NOT at the destination, immediately begin the Open Surfaces First sweep (above). Do NOT jump to closed storage until every open surface is exhausted.

### Semantic First-Target
After reading the task, identify the primary object's most likely surface or container. Make your first "go to" action target that surface. Only fall back to exhaustive exploration if the inferred location yields nothing.

### Sequential Container Search
When searching a series of like containers (e.g., cabinet 1 through cabinet 13), inspect them in logical order (numeric or alphabetic). Open one, note its contents, then move to the next adjacent container. Do not skip to a non-adjacent container unless you have a specific reason to believe the target is there.

### Grab on Sight
At each new location, immediately scan the admissible actions for any "take <target_object> from <location>" entry. If present, take the object now. Do not note it and return later—deferring pickups causes costly revisits. Before taking, verify that the object's name exactly matches the target object from the task description.

### Multiples: Containers First
When the task requires two or more of an object type (e.g., "two saltshakers"), prioritize closed storage (cabinets, drawers, fridges) over open surfaces—but still exhaust open surfaces before opening any container. Small multiples often live together in containers.

### Destination-First Sweep
When the task requires placing an object into a specific receptacle type (e.g., stoveburner, shelf, drawer), visit EVERY instance of that receptacle type before opening any storage containers. Only after exhausting all instances of the target receptacle type should you begin the Open Surfaces First sweep, then closed containers.

### Search Priority (Reinforced)
Always follow the CRITICAL: Search Priority Order from the Core Approach: **open surfaces first**, then closed containers. Include any target location in your open-surface sweep. Before opening any closed container, verify all open surfaces from the initial observation have been visited.

### Never Revisit Exhausted Locations
Maintain an explicit CHECKED list of locations you have already confirmed do not hold the target. Before each "go to X" or "open X" action, scan your CHECKED list. If the location is on it, skip it and choose an unvisited destination. Runtime check: "Is X on my CHECKED list?" If yes, choose an unvisited destination instead.

### Semantic First-Target
After reading the task, identify the primary object's most likely surface or container. Make your first "go to" action target that surface. Only fall back to exhaustive exploration if the inferred location yields nothing.

### Container Type Prioritization
When searching closed containers, prioritize the container type most semantically associated with the target object (e.g., drawers for utensils like knives/forks/spoons, cabinets for dishes/plates, fridge for perishable food). Exhaust all instances of that type (e.g., all drawers) before moving to other container types. Runtime check: before opening a container of a different type, ask "Have I opened and inspected every instance of the current container type?" If not, continue with the next instance of that type.

### Sequential Container Search
When searching a series of like containers (e.g., cabinet 1 through cabinet 13), inspect them in logical order (numeric or alphabetic). Open one, note its contents, then move to the next adjacent container. Do not skip to a non-adjacent container unless you have a specific reason to believe the target is there.

### Grab on Sight
At each new location, immediately scan the admissible actions for any "take <target_object> from <location>" entry. If present, take the object now. Do not note it and return later—deferring pickups causes costly revisits.

Before taking, verify the object's name against the target. If the target is a compound noun (e.g., butterknife, saltshaker) and the observed object's name is the base noun (e.g., knife, shaker), treat it as a candidate: take it and attempt to use it for the task. If the action fails, then search for a more specific object. Do not take clearly unrelated objects (e.g., 'pot' when you need 'pan').

Once you have the target object in inventory, stop searching for it and proceed directly to the goal location. Do not search for additional instances or alternative versions of the same object unless the task explicitly requires multiple copies.

### Multiples: Containers First
When the task requires two or more of an object type (e.g., "two saltshakers"), prioritize closed storage (cabinets, drawers, fridges) over open surfaces—but still exhaust open surfaces before opening any container. Small multiples often live together in containers.

### Destination-First Sweep
When the task requires placing an object into a specific receptacle type (e.g., stoveburner, shelf, drawer), visit EVERY instance of that receptacle type before opening any storage containers. Only after exhausting all instances of the target receptacle type should you begin the Open Surfaces First sweep, then closed containers.

### Small Objects: Open Surfaces First
Small portable objects (knives, forks, apples, phones, keys, pens) are far more likely to rest on countertops, tables, and open shelves than inside closed storage. When searching for any small object, inspect EVERY open surface in the room before opening a single cabinet, drawer, or closed container.

### Post-Container Surface Check
After opening any closed container and confirming the target object is not inside, pause before opening the next container. Review the current admissible "go to" list for any unvisited surface-type locations. If any surface remains unvisited, go there next. Do not open a second closed container until every reachable surface has been checked.

## Search Strategy

### 1. Target-First Check
When the task involves placing an object into a target location, go there FIRST. If the target is there, take it. If not, note its absence and proceed. When visiting the destination early, open it if closed — this saves a step later.

### 2. Destination-Type Sweep
When placing into a specific receptacle type (e.g., stoveburner, shelf), visit EVERY instance of that type before opening storage. Only after exhausting all target-type instances, begin the surface sweep.

### 3. Open Surfaces First — Before Any Closed Container (CRITICAL)
At the start of any search, visit EVERY open surface listed in the initial observation (countertops, tables, shelves, desks, sidetables, beds, diningtables, garbagecans, stoveburners) before opening a single drawer, cabinet, or other closed container. Small objects (plates, mugs, phones, utensils) are far more likely on open surfaces than inside drawers. This is a hard rule — no exceptions based on semantic guesses about where an object "should" be.

**Runtime check:** before your first `open <container>` or `go to <closed-container>`, confirm all surface-type locations have been visited. If any remain, go there next. After any closed container check fails to find the target, immediately resume the open-surface sweep before opening another closed container.

### 4. Closed Containers — Systematic Sweep
Only after exhausting all open surfaces, open closed containers in logical numeric order. Complete one container type before switching (e.g., all drawers before cabinets). Open at least half the instances of a type before abandoning it. When searching, progress sequentially: drawer 1 → drawer 2 → … → drawer N. Never skip to revisit an already-opened empty container.

**Container Type Prioritization:** prioritize the type most semantically associated with the target (drawers for utensils, cabinets for dishes, fridge for perishables). Exhaust that type before moving to others.

### 5. Never Revisit Exhausted Locations (CRITICAL)
Maintain a written CHECKED list: "CHECKED: [location] — no [target]." Before every `go to X` or `open X`, scan the list. If X is on it, skip it. Only revisit if you placed something there. This is especially critical for drawers and cabinets: once opened and found empty, never return without cause.

### 6. Post-Container Surface Check
After opening a container and confirming the target is absent, pause. Check the admissible `go to` list for unvisited surfaces. If any remain, go there before opening another container.

### 7. Grab on Sight
At each new location, immediately scan admissible actions for `take <target> from <location>`. If present, take it NOW — do not defer. Verify the object name matches the target. For compound nouns (butterknife, saltshaker), accept base-noun candidates (knife, shaker) and attempt use; if it fails, search for the specific object. Once the target is in inventory, stop searching and proceed to the goal.

### 8. Multiples: Containers First
When the task requires two or more of an object, prioritize closed storage — but still exhaust open surfaces first. Small multiples often live together in containers.

### 9. Deliver Immediately After Pickup
After taking a target object, check if a direct "move [object] to [target receptacle]" action is admissible. If so, execute it immediately. If not, navigate directly to the goal receptacle and place it before searching for anything else. Do not accumulate objects in inventory. **Runtime check:** while holding a target object, confirm the admissible `move` action points to the goal receptacle; execute it before picking up anything else.
## Action Validity & Recovery


### Take Before Use
When a task requires using a functional object (e.g., lamp) to examine a target object, ALWAYS take the target object into inventory FIRST. Only THEN activate or use the functional object. Before any "use" action, verify: "Is the target object already in my inventory?"

### When to Use Examine
When you arrive at a receptacle and the observation explicitly lists its contents (or states "you see nothing"), treat that information as definitive. Do NOT waste a step on "examine" to re-read the same content. Use "examine" only when the arrival observation does not describe the receptacle's contents. Runtime check: after arriving, if the observation contains "On the X, you see [list or nothing]", skip examine and decide your next action immediately. If the text says "The [container] is closed", emit "open [container]" as your next action, not "examine".

### Direct Appliance Actions
When at an appliance (microwave, stove, toaster) while holding an object that needs heating or cooking, scan the admissible actions for a direct "heat/cook <object> with <appliance>" command. Use it immediately if available. Do not manually place the object into the appliance first.

### Immediate Placement
When holding the prepared object, scan the admissible actions for a direct "move [object] to [goal receptacle]" action. If present, execute it immediately — do not navigate to the destination first. If no direct move is available, navigate to the destination and then place. Do not perform extra examinations or navigation steps once the object is ready and the move action is available. Runtime check: after any transformation or pickup, if the goal destination is known, check for a "move [object] to [destination]" action in the admissible list. If it exists, select it without any intervening navigation.

Example: after cleaning an apple at sinkbasin, if "move apple to diningtable 1" is admissible, use it directly instead of going to diningtable 1 first. Similarly, arriving at sidetable 1 holding mug 1 with 'move mug 1 to sidetable 1' in the admissible list → execute it immediately. Do not examine the sidetable first.
### Inventory Verification
Before executing a task-specific action at a target location (e.g., cleaning at a sink, placing on a shelf), confirm you are holding the required object. Use the `inventory` action to verify. If the required object is not in inventory, locate and pick it up first.

### Recovery: Nothing Happens
When `go to <receptacle>` results in "Nothing happens," immediately use `examine <receptacle>` to confirm its contents before navigating elsewhere.


### Direct Appliance Actions (Critical)
When at a heating or cooling appliance (microwave, stove, toaster, fridge) holding an object that needs heating, cooking, or cooling, scan the admissible actions for a direct "heat/cook/cool <object> with <appliance>" command. Use it immediately if available. Do NOT open the appliance, place the object inside, or close the appliance first. Example: holding an apple at a closed microwave, use "heat apple with microwave" directly — never open → move → close → open → take → heat. Example: holding bread at a fridge, use "cool bread with fridge" directly. Failure: agent placed apple inside microwave before heating, causing unnecessary steps. Runtime check: before opening any appliance, scan admissible actions for a combined heat/cook/cool action involving the object you are holding.

NEVER perform the open→place→close→open→take→heat/cool cycle when a direct combined action is available. If the admissible list contains "heat/cook/cool <held_object> with <appliance>", use it immediately. Do not open the appliance, do not place the object inside, do not close it, do not reopen it, do not take the object back out. One action, not five.
### No Redundant Examine After Finding Target
When an observation explicitly lists the target object as visible in a container or on a surface, take it immediately. Do not re-examine the same location — the observation that revealed the item is sufficient evidence to act.

### Deliver Immediately After Pickup
After taking a required object, check if a direct "move [object] to [target receptacle]" action is admissible. If so, execute it immediately. If not, navigate directly to the target receptacle and place it. Do not hold the object while exploring other locations. Runtime check: after a successful `take` action, scan admissible actions for a "move [object] to [goal receptacle]" command. If present, use it; otherwise, go to the target receptacle.

### Immediate Pickup on Sighting
When the observation lists a target object and a "take <object> from <location>" action is admissible, execute it immediately. Do not examine the location or perform any other action first. This applies whether the object is on an open surface or inside an opened container.


### Closed Container → Open Immediately
### Closed Container → Open Immediately (CRITICAL)
When arriving at any closed container (drawer, cabinet, fridge, microwave, etc.) and the observation states it is closed, always take the "open [container]" action immediately — no intervening "examine" step. Never assume a closed container does or does not contain a needed object. Open it first, then inspect. Do not leave without opening. Failure example: agent went to cabinet 1, saw it was closed, and left without opening — missing the target inside. Runtime check: if the observation contains "[container] is closed" and "open [container]" is admissible, select "open [container]" directly. Before attempting to take or examine an object from any container, confirm the action history shows you have already opened it. This applies during search, during destination checks, and before any placement into a container.

### Verify Held Object Before Tool Use
When you pick up an object and plan to use a tool (lamp, appliance, etc.) on it, first check if `examine <held-object>` is admissible. If it is, examine the held object to confirm its identity before navigating to the tool. This prevents using the wrong object or assuming an incorrect state. Runtime check: after taking an object, scan admissible actions for `examine <object>`. If present and you intend to apply a tool to it, execute the examine first.


### Skip Examine When Contents Are Visible
When an observation already describes a container's or surface's contents (e.g., "On the cabinet 1, you see nothing" or "In the drawer, you see a fork"), do NOT emit an examine action. The observation has already given you the full contents. Only use examine when the observation does not describe what is on/in the location. Runtime check: "Does the current observation end with 'you see ...' or 'In it, you see ...'? If yes, skip examine and act on that information immediately."

Example: after picking up toiletpaper and arriving at toiletpaperhanger, immediately use `move toiletpaper to toiletpaperhanger` — no examine, inventory, or look steps.
## Task-Type Procedures


### Clean-and-Deliver Tasks
For tasks requiring a cleaned object (e.g., "put a clean X in Y"): decompose into explicit ordered subgoals: (1) locate the object, (2) take the object, (3) navigate to a sinkbasin or bathtub, (4) execute "clean X with sinkbasin", (5) navigate to the target receptacle, (6) place the object. Never go to the target receptacle before cleaning is complete. Runtime check: after reading the task, restate the sequential subgoals and confirm the cleaning step is included before taking any placement action.

### Heat-and-Deliver Tasks
### Heat-and-Deliver / Cool-and-Deliver Tasks
When the task requires heating or cooling an object and placing it in a target receptacle, follow this direct cycle without deviation:
1. Go to the object's location
2. Take the object
3. Go to the appliance (microwave, stove, fridge, etc.) — do NOT set the object down elsewhere first
4. Execute the transformation action (heat/cool) immediately
5. Go to the target receptacle
6. Place the object

**CRITICAL: Transform before placing.** After taking the object, go straight to the appliance and use its transformation action. Never place the object on a surface or back where you found it before transforming. Runtime check: after picking up an object, ask "Does the goal mention a state like 'cool', 'hot', 'heated', or 'chilled'?" If yes, do not set the object down until you have performed that transformation.

Do not search rooms, open cabinets, or investigate unrelated objects once the target object and receptacle are known. Execute the sequence immediately.


Runtime check for clean tasks: before placing the object in the target receptacle, confirm "Does the task description contain the word 'clean'? If so, have I used a sink or cleaning appliance on the object?" If cleaning hasn't happened yet, go to a sinkbasin and execute the clean action first.


**Cooling-Specific Optimization**: For cooling tasks, make the fridge your very first destination. Go to the fridge and open it before searching for the target object. This prepares the appliance and saves a step. Runtime check: after reading the task, if it includes "cool" or "chilled", confirm your first action is `go to fridge` (or the cooling appliance) and then `open` it.

**Cooling example**: If the task is "cool some pot and put it on countertop", after taking the pot, go to the fridge and use the direct action `cool pot 2 with fridge 1` (or similar). Do not open the fridge and place the pot inside.
### Direct Cleaning Actions
When at a cleaning fixture (sinkbasin, bathtub) holding an object that needs cleaning, scan the admissible actions for a direct "clean <object> with <fixture>" command. Use it immediately if available. Do NOT place the object onto the fixture first. Runtime check: before any "put" or "place" action at a cleaning fixture, verify that no direct "clean" action is admissible for the held object.

### Post-Heating Pickup (MANDATORY)
After executing a heat/cook action at any appliance, immediately verify the heated object is in your inventory. If the observation does not explicitly list it as held, take it from the appliance before moving to the next destination. Runtime check: after the heat confirmation, ask "Is the heated object in my inventory?" If not, take it NOW before any `go to` action. Never leave the appliance area without the heated object in hand.

### Look-at-Under-Light Tasks
When the task goal is "look at X under the Y" (where Y is a light source like desklamp or floorlamp), follow this exact order:
1. Go to X's location and take X into inventory
2. Go to Y's location
3. Use/activate Y
Do NOT activate the light before holding the target object. Runtime check: after reading the task, ask "Is the goal 'look at OBJECT under LIGHT'? If so, have I taken OBJECT before activating LIGHT?"
## Common Pitfalls


- **Skipping open surfaces:** Going straight to cabinets/drawers before checking countertops, tables, shelves. Always follow Search Priority Order: target → target-type instances → open surfaces → closed containers.
- **Revisiting empty locations:** Returning to a location on your CHECKED list without cause. Concrete failures: agent revisited fridge 9 times, cabinet 1 four times, cabinet 2 three times. Maintain and consult the CHECKED list before every navigation action.
- **Leaving closed containers unopened:** Navigating to a closed container, seeing it is closed, and leaving without opening it. Always open a closed container immediately upon arrival if you haven't found the target yet. Failure example: agent went to cabinet 1, saw it was closed, and left — missing the target inside.
- **Revisiting the target container after initial check:** After checking the target location (especially if it's a closed container like a fridge) and not finding the object, add it to your CHECKED list immediately and do not return until you are holding the prepared object. Revisiting before exhausting all open surfaces is a common error that wastes steps.
- **Holding objects during search:** Keeping a found object while searching for others. Deliver each item to the goal receptacle immediately after pickup.
- **Leaving heated/cooled objects behind:** After transformation at an appliance, navigating away without the object. Confirm it is in inventory before moving.
- **Mid-search inventory checks:** Using `inventory` when nothing was picked up. Only verify after a `take` or before a transformation step.
- **Searching the transformation appliance for the base object:** The appliance is where you transform, not where you find the object. Never search a fridge for bread when the goal is "cool bread" — find bread elsewhere, then bring it to the fridge.
- **Post-completion looping:** After executing the final placement action (e.g., "move butterknife to drawer"), STOP immediately. Do not take any further actions, even if the admissible list still includes "take" for the object you just placed. Once the task goal is satisfied, the task is complete. Runtime check: "Have I just performed the action that fulfills the task description?" If yes, take no further actions. If the observation confirms the final placement, do not interact with the object again.
- **Repeating uninformative actions:** Repeating examine/look when nothing changed. After one uninformative result, change context.
- **Ignoring landmark activation verbs:** When the goal mentions a landmark (e.g., "under the DESKLAMP"), scan for "use <landmark>" or "turn on <landmark>" and execute it.
- **Premature destination opening:** Opening the target receptacle before holding the prepared object. Exception: opening during the initial target-first check is acceptable and recommended. Otherwise, defer opening until you hold the prepared object at the destination.
- **Placing into closed containers:** Attempting `put/move` into a closed container. Confirm it is open first; if closed, `open` it, then place.
- **Returning to a previously sighted copy without systematic search:** After placing one copy of a multiple-object task, immediately going back to a location where you previously saw another copy without first checking other unvisited surfaces and containers. Instead, treat the search for the next copy as a fresh search: visit all unvisited locations before revisiting any previously inspected location. Runtime check: after depositing one found item, look at your list of admissible movement actions and pick a destination you have not yet visited (or not yet opened) before revisiting any location you already inspected.
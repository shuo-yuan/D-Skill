---
name: alf
description: "Embodied household-task skills distilled from execution experience."
---

## Core Approach


Verify object identity and state before acting. After picking up an item, if `examine <held-item>` is admissible, perform it before traveling to use a tool on it.

Use the task goal to prioritize navigation targets. Before acting, identify the most semantically associated surface or container for each target object (e.g., bowls → desks/tables/shelves, lamps → desks/side tables). Navigate to the most promising receptacle first rather than exploring randomly.

## Task Decomposition

Decompose the task into a linear sequence of subgoals: locate target object → take it → process it at the appropriate station (if needed) → deliver it to the target receptacle. Before moving to a new location, confirm that the current step advances you toward the next subgoal rather than detouring. Execute each subgoal directly; do not wander or inspect unrelated objects.



For tasks requiring multiple objects to be placed in the same receptacle (e.g., 'put two newspapers on the sofa'), deliver each object immediately upon acquisition: take the object, go to the receptacle, and place it before searching for the next object. Do not accumulate multiple objects in inventory.

After acquiring a target object, go directly to the destination receptacle and place it, unless a transformation is required. Do not stop to inspect other objects or revisit locations. Runtime check: after a successful `take`, verify that your next `go to` destination is the target receptacle named in the task description. If not, redirect to the destination before any other movement.

Before taking the first action, state the ordered sub-goals explicitly in your reasoning. After each action, verify it advances you toward the next unmet sub-goal. If an action does not directly serve the current sub-goal, redirect immediately.

Self-check before each action: 'Is this next action directly related to one of the objects named in my task goal?' If not, redirect to an action that advances the search for or processing of a named object.
## Precondition Chains


Before performing the final interaction (e.g., use, examine, put) that involves multiple objects, verify all required objects are located and, if needed, activated or in inventory. Read the task instruction and list all distinct objects. For each, ask: "Have I seen this object in an observation or is it in my inventory?" If any object is still unseen, prioritize searching unexplored surfaces/containers rather than repeatedly interacting with objects you already have. Only proceed when all objects are accounted for.

**Acquire before destination**: When the goal requires placing an object into a receptacle, first locate and acquire the object, perform any required transformations (clean, heat, cool), and only then identify and navigate to the destination receptacle. Do not open or evaluate potential destinations until you are holding the target object. Runtime check: before opening or moving to a destination, confirm via inventory that you hold the target object. If not, redirect to search.


Exception: If the destination receptacle is a surface where the object could plausibly be located (e.g., stoveburner, countertop, table), first visit all instances of that receptacle type to check if the object is already there, before searching storage. This overrides the acquire-first rule for surface destinations. After checking all such instances and not finding the object, proceed directly to closed storage containers (drawers, cabinets) rather than exhaustively checking other open surfaces.
## Search Strategy


**Destination-first for 'put' tasks (MANDATORY)**: When the task is to 'put X in/on Y', make Y the very first location you visit. Go there before any other search action. Check its contents; if X is already there, take it and place it back to complete the task. If not, note what else is present and proceed with surface-first search. Runtime check: before your first move away from the starting position, ask 'Have I visited the target receptacle Y yet?' If not, go there immediately.


**Surface-first (MANDATORY)**
  - **Runtime check before first search**: When you first plan to find an object, scan the admissible action list for `take` actions involving visible surfaces from the initial observation. If none exist because you haven't navigated to those surfaces yet, visit them first and let their observations reveal `take` options before resorting to opening drawers or cabinets.: Before opening any closed storage, inspect ALL visible open surfaces (countertops, tables, basins, stoveburners, shelves) listed in the room description. Do not open any cabinet, drawer, or fridge until EVERY visible surface has been visited. For example, when searching for a mug, check dining tables, countertops, coffee tables, and desks before opening cabinets. At each step, check admissible actions: if any unvisited open surface remains, prioritize visiting it over opening a closed container. After inspecting an open surface, do not revisit it. Self-check before opening any closed container: 'Have I visited every countertop, table, and shelf in this room?' If not, go to the next unvisited surface.

**Target-receptacle priority**: If the task involves placing an object into a specific receptacle (e.g., 'put a hot potato in the fridge'), search that receptacle first before exhaustively checking other containers. The object may already be there. Runtime check: Before navigating to a storage location, ask: 'Is the target receptacle a plausible location for the object?' If yes, go there first.

**After target-receptacle check**: If the object is not found in the target receptacle, immediately apply the surface-first rule: visit all open surfaces (countertops, tables, diningtables, etc.) in the room before revisiting any closed container, including the target receptacle. Do not return to the target receptacle until every surface and other container type has been exhausted. Self-check: 'Have I visited every open surface since checking the target receptacle?' If not, go to the next unvisited surface.

**Systematic container search**: When searching closed storage, first list all container types from admissible actions (shelves, drawers, cabinets, etc.). Exhaust each type completely in a fixed spatial order (e.g., top-to-bottom, left-to-right) before moving to the next type. Track which containers you have opened and found empty; never revisit an empty container unless you have exhausted all other container types or have new information (e.g., object was moved there). Always open a closed container before inspecting it; if the object isn't visible, use `examine <receptacle>` to confirm emptiness.

**No-revisit rule**: Maintain a mental list of every container you have opened and what it contained. Do not revisit a container unless you have reason to believe its contents changed or you need an object you know is inside. Before each 'go to' action, check: "Have I already opened this container and recorded its contents?" If yes and you have no new information, skip it.




**Room-entry checklist**: Upon entering a new room, immediately scan the observation text for all visible open surfaces (countertops, tables, desks, shelves, stoveburners, diningtables). List them and visit every one before opening any closed container. Runtime check: 'Have I visited every visible table-like surface in this room?' If not, do not open a cabinet, drawer, or fridge.



**Target-receptacle instance survey**: Before any storage search, first visit all instances of the destination receptacle type (e.g., all stoveburners) to check if the object is already there and to identify empty receptacles for later placement.

**Multiple-object search**: When the task requires multiple copies of an object (e.g., 'put two newspapers on the sofa'), after finding and placing one copy, do not immediately return to the location where you previously saw another copy. Continue systematic search of unvisited surfaces and containers first. Only revisit a known source after exhausting all other plausible locations in the room. Runtime check: after depositing one found item, list admissible movement actions, pick a destination you have not yet visited (or not yet opened, if a container), and go there before revisiting any location you already inspected.

**Open on arrival**: During search, when you navigate to a receptacle and the observation states it is closed, your immediate next action must be to open it and inspect its contents before moving elsewhere. Never leave a closed container unopened.

**Initial surface match**: Before any movement, scan the initial room description for the name of the surface most associated with the target object (e.g., 'desklamp' → 'desk'). If that surface appears in admissible actions, navigate there first. Do not search other containers until this surface has been inspected.
If the object is not found on that surface, systematically visit all remaining surfaces in a fixed order (e.g., alphabetical or spatial) before opening any closed container.


**Post-container surface check**: After opening a closed container and not finding the target object, revisit the list of unvisited open surfaces (countertops, tables, shelves, diningtables, etc.) from the room description and current admissible actions. If any remain unvisited, visit them before opening another closed container. Runtime check: 'Have I checked every surface location I can go to?' This prevents skipping surfaces like diningtables that are the target receptacle.


**Container-type exhaustion**: When searching closed storage, group all instances of one container type (e.g., all drawers, then all cabinets). Exhaust every instance of the current type before moving to the next type. Runtime check: before switching container types, ask: 'Have I opened and inspected every instance of the current container type in this room?' If not, continue with the next unvisited instance of the same type.


**Ambiguous-move recovery**: If `go to <receptacle>` results in "Nothing happens," immediately use `examine <receptacle>` to confirm its contents before deciding your next action.


Runtime check: Before taking an object from a container, confirm the action history shows you have already opened that container in the current visit. If not, open it first.




**Complete sweep before revisiting**: Before revisiting any location, ensure you have visited every admissible `go to` destination in the current room at least once. Maintain a written list of unvisited destinations (all surfaces, furniture, containers, appliances) from the current admissible actions. Cross off each after visiting. Only after exhausting all destinations once may you consider revisiting previously checked locations. Runtime check: before each `go to` action, scan the admissible actions for any destination not yet visited; if found, go there first.

**Multi-object exception to surface-first**: When the task requires two or more copies of an object (e.g., 'put two saltshakers on the counter'), storage containers (cabinets, drawers, fridges) often hold multiples. After checking the most semantically associated surface (e.g., saltshaker → countertop), prioritize opening one storage container type before exhaustively scanning all remaining open surfaces. Runtime check: 'Does the task require multiple copies? If yes, have I opened at least one cabinet or drawer yet?' If not, open one before visiting every diningtable and sidetable.

**Explicit checked-and-empty list**: At the start of each room search, write down every visible surface and container from admissible actions. As you visit each, mark it as checked with its contents or 'empty'. Before every `go to` action, consult this list: if the target location is marked as checked-and-empty, skip it and choose the next unvisited location. This list is your single source of truth — do not rely on memory alone.
## Action Validity & Recovery


### Direct Actions and Receptacle Handling
- **Direct actions without pre-opening**: When an admissible action directly accomplishes a subgoal (e.g., `heat`, `cook`, `cool`), use it immediately without any intermediate placement or opening steps. Do not manually place the object into the appliance; prefer the direct `heat <object> with <appliance>` action if available. Check: 'Does the admissible list contain a direct action that matches my subgoal?' If yes, skip the `open` and placement steps.
- **Object placement**: Do not place the object inside the appliance before using a direct action (e.g., heat, cook, cool). Use the action while holding the object; never open the appliance or move the object into it first.
- **Post-heating**: After heating, take the heated object from the appliance, then proceed to placement; do not re-examine or re-open unnecessarily.
- **Destination receptacle timing**: Open the destination receptacle early (before searching for the target object) if it is accessible and appears in admissible actions. This saves a step at the end. If a direct 'move' action is available (e.g., 'move object to receptacle'), use it; otherwise, ensure the receptacle is open before placing.
- **Container state check (MANDATORY)**: Before any `take`, `examine`, or content inspection on a container, verify it is open. If `open <container>` appears in admissible actions, the container is closed—open it immediately. This applies to drawers, cabinets, fridges, microwaves, and any other closed storage. Never attempt to examine or take from a closed container. Self-check: 'Is `open <container>` in admissible actions?' If yes, open it first.

- **Direct manipulation without placement**: When at a location holding an object and an admissible action directly manipulates it (e.g., `clean <obj> with <fixture>`, `heat <obj> with <appliance>`), execute that action immediately; do not first place the object at the location.

- **Inventory verification before action**: Before performing a task-specific action (e.g., clean, heat, place), confirm you are holding the required object using the `inventory` action. After traveling to a target location, ask: "Am I certain I am holding the target object?" If not, use `inventory` to verify.


- **Closed appliance, direct action**: When a direct action (e.g., `cool`, `heat`, `cook`) involving a closed appliance is admissible, use it immediately. Do not open the appliance first—the direct action handles the opening implicitly.
## New Section
## Task Completion


## Task-Type Procedures


### Transformation Tasks
For any task that requires transforming an object (heat, cool, clean, etc.), follow this general sequence: (1) locate and take the base object, (2) move to the appropriate appliance, (3) apply the transformation, (4) take the transformed object from the appliance, (5) move to the destination, (6) place. Do not search for the transformed object inside the appliance; search for the base object first.

- **Heat and Place**: Specific sequence: go to storage, take object, go to heating appliance, heat (use direct action if available), take heated object, go to destination, place.
- **Cleaning**: If the task mentions 'clean' before an object, clean it at a sink or appropriate fixture before moving to the destination. Self-check: 'Have I already performed the cleaning action?'


**Direct Heat-and-Deliver Cycle**: When the target object and destination receptacle are known, execute without deviation: (1) go to object, (2) take it, (3) go to appliance, (4) heat it, (5) go to destination, (6) place it. Do not re-examine or re-open appliances after heating.


### Look-at-Object-in-Light Tasks




**Cooling tasks: fridge-first preparation**: When the task requires cooling an object, make the cooling appliance (fridge) your first destination. Go to the fridge and open it before searching for the target object. This prepares the appliance so it is ready immediately once you acquire the object. Runtime check: after reading a task involving "cool" or "chill," verify your first action targets the fridge.
## Common Pitfalls


- **Fixating on a single object**: When the task involves two objects (e.g., 'examine X with Y'), do not repeatedly examine or move X alone. Instead, search for Y systematically until found, then bring them together or activate Y before attempting the goal action.
- **Transformation before placement (mandatory)**: When the task specifies a transformation (clean, heat, chill, slice) followed by placement, perform the transformation while holding the object *before* moving to the destination receptacle. Do not place the object anywhere until the transformation is complete. After taking the object, go directly to the appliance and use the transformation action (e.g., `cool bread 1 with fridge 1`). Runtime check: after picking up an object, ask 'Does the goal require a state change (cool, hot, clean, sliced)?' If yes, do not set the object down until you have performed that transformation. Confirm success before any `put` or `move` to the destination.
- **Closed container assumption**: Never assume a closed container is empty. Open it first, then inspect contents.

- **Redundant examine or re-examining**: When an observation already lists the target object in a container or on a surface, act on it immediately (take/pick up). Do not re-examine the same location — the observation that revealed the item is sufficient evidence. Similarly, when you arrive at a receptacle and the observation explicitly lists its contents (or says 'you see nothing'), treat that as definitive; skip `examine` and decide your next action immediately. Self-check: 'Did the last observation already show the object I need?' If yes, take it now without an intervening look or examine.

- **Leaving appliance without taking transformed object**: After heating, cooling, or cleaning an object, the transformed object is inside the appliance. Always take it before moving to the next location. Check inventory to confirm possession before leaving.



- **Picking up irrelevant objects**: When searching for a specific target object, only take the object whose name exactly matches the target name from the task description. Before issuing a `take` action, verify: 'Is this the exact object I need to complete the current subgoal?' If not, leave it and move on to the next location.


- **Leaving target object behind**: When you observe the target object at your current location and a 'take [target] from [location]' action is admissible, take it immediately. Do not leave it behind to continue searching other locations. After taking it, proceed directly to the target receptacle to place it — no intermediate detours. Self-check: 'Does the observation contain the task-relevant object?' If yes, confirm your next action is 'take [object] from [surface]' followed by a move to the target receptacle.


- **Uninformative feedback loop**: If an examine or look action returns a generic or non‑informative observation (e.g., "nothing special"), do not repeat that exact action on the same object or surface. Instead, move to a different location or use a different admissible action.


- **Ignoring partial name matches**: When the task mentions a specific object (e.g., 'butterknife') and you observe an object whose name contains the key noun (e.g., 'knife 1'), treat it as the target. Take it, perform any required transformation, and deliver it. Do not continue searching unless the action fails or the task explicitly requires a different object. Self-check: 'Does this observed object's name contain the target keyword?' If yes, act on it immediately.


- **Drawer-first search bias**: When the target object is not immediately visible, do not default to searching drawers or cabinets. Always exhaust all visible open surfaces (sidetables, coffeetables, desks, shelves, countertops) first. Drawers and cabinets are last-resort storage. Self-check before opening any drawer: 'Have I visited every table, desk, and shelf in this room?' If not, go to the next unvisited surface.
- **Indecision when multiple matching objects are visible**: When multiple instances of the required object type are visible, immediately take the first one listed in admissible actions rather than deliberating or searching elsewhere. Runtime check: after arriving at a location, scan the `take` actions for any item matching the task object type; if at least one exists, take the first listed instance and proceed.
- **Examining closed containers**: When you arrive at a container and the observation states it is closed, do not use `examine` on it; open it directly. The `examine` action on a closed container provides no useful information and wastes a step.
- **Unnecessary actions after acquisition**: After picking up the target object, immediately navigate to the destination and place it. Do not examine, inventory, or close containers. Runtime check: if the observation says 'You pick up [target object]', the next action must be 'go to [destination]'.
- **Search looping**: If you catch yourself returning to a location you already visited and found empty, stop immediately. Review your checked-and-empty list, pick the next unvisited location from the initial room description, and go there. Never revisit a checked-and-empty location unless you have new information (e.g., you just placed something there).

- **Non‑sequential container search**: When multiple instances of the same container type exist (e.g., cabinet 1, cabinet 2, …), open them in numerical or alphabetical order. Do not jump to a non‑adjacent container unless you have already opened all lower‑numbered ones. Before moving to a cabinet, check if any unvisited cabinet with a lower number remains; if yes, go there first.
- **Revisiting exhausted categories**: After you have opened every drawer in a room and found them all empty, do not return to any drawer. The same applies to cabinets, shelves, or any other container type. Once a category is fully checked and empty, it is locked out. Before moving to a drawer/cabinet/etc., confirm you haven't already exhausted that entire category.
- **Redundant examine after opening**: When you `open <container>`, the observation that follows already reveals its contents (or emptiness). Do not follow an `open` with `examine` on the same container. Similarly, if the arrival observation after `go to <location>` already says 'In it, you see...' or 'On it, you see...', do not `examine` that location. Self-check: 'Did the last observation already tell me what's inside/on this?' If yes, act on that information without an extra `examine`.
- **Holding found items during continued search**: When the task requires multiple objects (e.g., 'put two keychains on the armchair'), deliver each object to the goal receptacle immediately upon finding it. Do not hold one object while searching for the next. Runtime check: after a successful `take` of a target object, if the task requires multiple copies, your next action must be `go to <goal receptacle>` (or `move <object> to <receptacle>` if already there).
- **Hesitating at target location**: When you arrive at a location and the observation shows the target object is present and a `take` action is admissible, take it immediately. Do not examine, look around, or deliberate — secure the object first, then plan the next step.
---
name: alf
description: "Embodied household-task skills distilled from execution experience."
---

## Core Approach


When the target object is visible in the observation and a "take" action is admissible, pick it up immediately. Do not examine the location or take other actions first — acquire the object as soon as it is identified.

Prefer direct actions over multi-step physical manipulation when both are available. For example, use "cool X with Y" to cool a held item rather than opening the appliance, placing the item inside, and closing it. Check the admissible actions list for these shortcuts before committing to longer interaction chains. **Hard rule:** If a direct verb+object+appliance action is admissible (e.g., 'heat tomato with microwave'), use it immediately — never open/place/close/take cycles.

### Object-to-Receptacle Mapping & Delivery
Before exploring, infer the likely location of each object from the task description:
- Personal items (pillow, book, phone) → beds, sofas, nightstands
- Tools and appliances (desklamp, mug, knife) → desks, tables, kitchen counters
- Storage items → drawers, cabinets, shelves

Use this mapping to plan a direct path: locate the target object, pick it up, go to the tool's expected home, and use the tool. Skip irrelevant containers and surfaces that do not match the inferred mapping.



At runtime, before navigating, ask: "What receptacle type commonly contains [target object]?" and prioritize that over generic storage or surfaces.


- After inferring the receptacle type, scan the initial room observation for the exact receptacle name (e.g., 'desk 1' for a desklamp) and navigate there first.

Before taking any action, decompose the task into ordered sub‑goals: (1) acquire the target object, (2) apply any required transformation, (3) deliver to the destination. State these sub‑goals explicitly and ensure each action advances you toward the next unmet sub‑goal.

Before each action, self-check: "Is this next action directly related to one of the objects named in my task goal?" If not, reorient to the task's core objects immediately.

- **Semantic-first navigation:** After reading the task instruction, identify the primary target object and infer its most likely surface or container (e.g., bowl → desk/table, pillow → bed, mug → kitchen counter). Make that receptacle your very first `go to` destination. Do not start with an arbitrary location from the admissible list — prioritize the semantically associated receptacle. Runtime check: "What surface or container is most commonly associated with [primary object]? Is my first `go to` action targeting that?"

While holding a target object, confirm that the only admissible `move` action points to the goal receptacle named in the task; execute it before picking up anything else.

- **Perishable food → fridge first:** When the target object is a food item commonly refrigerated (tomato, potato, lettuce, apple, egg, etc.), make the fridge your very first destination. Do not check cabinets, countertops, or other storage before the fridge. Runtime check: "Is the target a perishable food? If yes, go to the fridge immediately."
Always select actions from the admissible actions list provided. Never attempt an action that is not listed.

- Cutlery and small utensils (butterknife, spoon, fork, spatula) → drawers (exhaust all drawers before checking cabinets or surfaces).
## Precondition Chains

## Search Strategy


- **Surface-first search:** Prioritize open surfaces over closed containers. For small, commonly surface-placed objects (mugs, cups, plates, books, remotes), exhaust all visible surfaces first. For any search, visit every surface-type location (countertop, table, shelf, etc.) before opening any cabinet, drawer, or appliance. After opening a closed container and not finding the target, ask: "Have I checked every non-container location visible in the initial observation or current admissible go-to list?" If not, visit those surfaces next. Self-check: "Is there a visible surface I haven't inspected? If yes, go there first."


- **Immediate pickup:** If you spot the target object in any observation, take it immediately without re-examining the same location. At each new location, scan admissible actions for any "take <target_object> from <location>" and execute it without delay.
- **Container priority for collections:** When collecting multiple objects (e.g., "two saltshakers"), inspect storage containers (cabinets, drawers, fridges) early before exhaustively scanning all surfaces.
- **Exhaust similar receptacles:** When searching for a target object, exhaustively check all plausible receptacles of the same type (e.g., all beds, all desks) before moving to unrelated furniture. If the object is not immediately visible on a receptacle, use `examine <receptacle>` to confirm emptiness before leaving.
- **Direct-Path Execution:**
  1. Identify the task's implied object-to-receptacle mapping.
  2. Navigate to the first matching receptacle and check it.
  3. If not found, check the next most likely receptacle of the same type.
  4. Once acquired, proceed directly to the tool's expected location.
  5. Execute the tool action immediately.
  Runtime check: before each navigation step, confirm it directly serves locating the target object or the required tool. Do not explore unrelated containers or rooms.



- **Systematic container‑type exhaustion:** When the target is not on surfaces, identify all container types in admissible actions that could plausibly hold it (e.g., drawers, dressers, garbagecans). Systematically exhaust each type’s instances before moving to the next. Keep a mental log of inspected instances. Before re‑searching a previously inspected type, ensure you have exhausted at least half of the unexplored instances of the current type and ask: “What new containers have I not yet opened?” Use admissible actions to verify no numbered instances are missed.

- **Exhaust all visible locations before re-examining:** When a required object is not found in the first expected location, systematically visit every other location listed in the initial room observation before returning to or re-examining the first location. Runtime check: "Have I visited every other location from the initial observation at least once?"

- **Post-target-container surface sweep:** After checking the task's target receptacle (e.g., fridge for perishable food) and not finding the object, immediately visit every open surface listed in the initial observation (countertops, tables, diningtables) before opening any other closed container or revisiting the target receptacle. Do not return to the target receptacle until all surfaces have been exhausted. Self-check: "Have I visited every surface from the initial room description? If not, go to the next unvisited surface now."

Example: when you arrive at a desk and see 'cd 1' in the observation, immediately execute 'take cd 1 from desk 1' — do not examine the desk first.



- **Systematic surface sweep:** When multiple numbered instances of the same surface type exist (e.g., shelf 1, shelf 2, …), visit them in numeric order until the target is found. Do not skip to a different receptacle type before exhausting all instances of the current surface type.

- **Sequential like-container search:** When searching a series of same-type containers (e.g., cabinet 1 through cabinet 13), open them in numeric/alphabetical order. Do not skip to non-adjacent containers unless you have specific evidence the target is there. After opening one, move to the next sequential instance. This prevents missed containers and eliminates the need to backtrack later.

- **Destination-receptacle-first sweep:** When the task specifies a target receptacle type (e.g., "put X on stoveburner"), visit every instance of that receptacle type before searching for the target object in storage. Survey all stoveburners, all shelves, or all desklamps to check if the object is already present and to identify empty slots. Only after exhausting all destination receptacles should you begin searching cabinets, drawers, or other storage. Runtime check: "Have I visited every [destination receptacle type] in the admissible locations list?" If not, continue surveying destination receptacles before opening any storage container.

- **Multi-copy tasks — exhaust unvisited first:** When the task requires collecting multiple copies of the same object (e.g., "two newspapers"), after depositing one copy at the goal location, do NOT return to the location where you found the first copy. Instead, visit every other unvisited surface and container in the admissible locations list before revisiting any previously inspected location. Runtime check: "Have I visited every other location at least once since finding the first copy?" If not, go to an unvisited location now.


- **HARD SURFACE-FIRST RULE (applies before ANY closed container):** Before opening any drawer, cabinet, fridge, or other closed container, visit EVERY open surface listed in the initial room observation (desk, sidetable, countertop, table, shelf, diningtable, etc.). Take any target object found immediately. Only after confirming all surfaces have been visited and the target is not on any of them may you open a closed container. Self-check before any `go to` targeting a closed container: "Have I visited every surface from the initial observation?" If no, redirect to the next unvisited surface.


- **Surface-first after any negative check:** When you arrive at a surface and the target is not there, immediately scan the admissible `go to` list for the next unvisited open surface (sidetable, shelf, bed, countertop, diningtable, garbagecan) before considering any drawer, cabinet, or other closed container. Do not open a drawer or cabinet until every open surface from the initial room observation has been visited. Self-check: "Which open surfaces have I NOT yet visited?" and go there next.


- **Exhaust admissible list before any revisit:** When searching for a target object, before returning to any previously inspected location, verify that you have visited every location in the current admissible `go to` list at least once. If any location remains unvisited, go there first. Only after all locations have been visited once may you reconsider a previously empty one. Self-check: "Have I visited every location in the admissible list?"


- **Display objects on surfaces:** Statues, figurines, vases, and decorative items are almost always placed on open display surfaces (sidetables, coffeetables, shelves, mantles), never inside closed drawers or cabinets. When searching for any decorative or display object, exhaust all visible surface-type locations before even considering a closed container. Self-check: "Is the target a display-worthy object (statue, vase, decoration)? If so, have I checked every surface before opening any drawer or cabinet?"


- **Exhaust by receptacle type group:** Before any search, mentally group all admissible `go to` targets by type (countertops, stoveburners, cabinets, drawers, beds, desks, etc.). Visit every instance of one type group before moving to the next. Track which groups you have completed. Runtime check every 5 navigation actions: "Which receptacle-type groups have I fully visited? Which remain?" Do not skip a group unless you have visited every instance of it.


- **First admissible take:** When multiple instances of the target object type are visible (e.g., spoon 3, spoon 4), immediately execute `take` on the first one listed in admissible actions. Do not deliberate or search further.

- **Fixture-action scan at each new location:** When the goal requires interacting with a named fixture (e.g., desklamp, stove, sink), after arriving at each new location, scan the admissible actions list for any "use <fixture>" or "turn on <fixture>" action before taking any other step. If present, execute it immediately. Runtime check: "Does the admissible action list contain a 'use' or 'turn on' action for the goal fixture?" If yes, select it now.
- **Post-exhaustion redirect:** When you have visited every instance of a receptacle type group and found all empty, immediately move to the next unexplored receptacle type group. Do not revisit any instance of the exhausted group unless you later place an object there. Before any `go to`, check: "Have I already exhausted this entire receptacle type group?" If yes, skip all its instances permanently.
- **Immediate delivery for multi-copy tasks:** When the task requires multiple copies of an object and you find one, immediately go to the goal receptacle and `move` it there before resuming the search for the remaining copies. Do not hold the first copy while searching for others. Runtime check after picking up a target object in a multi-copy task: "Is there still another copy to find? If yes, deliver this one to the goal receptacle now, then resume search."
- **Utensil drawer priority:** When searching for a small tool or utensil (e.g., butterknife, spoon), treat drawers as the highest-priority container type. Exhaust all drawers before moving to cabinets or surfaces, overriding the general surface-first rule for these items.
- **Fixed spatial search sequence:** Before searching, build a fixed route from the admissible `go to` list: all open surfaces first (in numeric order), then all closed containers (in numeric order). Follow this sequence without deviation. After completing the full sequence once, only then may you loop back to the start — but skip any location already confirmed empty. Self-check before each `go to`: "Am I following my fixed sequence? Have I already inspected this exact location and found it empty?" If yes, advance to the next location in the sequence.
- **Never skip unopened containers for already-opened ones:** When progressing through closed containers, open every instance in numeric order. Do not revert to an already-opened, empty container while unopened containers remain in the sequence. Self-check: "Is there a closed container I haven't opened yet? If yes, go there next."
## Action Validity & Recovery


- **Open before inspect/take:** Always open a closed container before attempting to examine or take objects inside it. Upon arrival at any container that could reasonably contain the target, read the observation: if it states the container is closed (e.g., "The drawer 1 is closed"), use the admissible 'open' action for that container immediately as your next action. Do not examine it first or move elsewhere before checking inside. Never attempt 'take' or 'examine' on a closed container. **Hard rule:** If you arrive at a receptacle and the observation says it is closed, your next action MUST be to open it. Do not navigate away from a closed container without opening it first. Self-check: "Does this observation say 'The X is closed'? If so, my next action must be 'open X'."
- **Immediate take:** When you observe the target object at your current location and a "take [target] from [location]" action is admissible, execute that take action immediately before moving to another location. If you consider going elsewhere, stop and take the object first.
- **Transformation before placing:** After picking up an object, check if the goal requires a state change (cool, heat, slice, clean, etc.). If yes, go directly to the relevant appliance and perform the transformation before placing the object anywhere. Never set the object down until its state matches the goal.
- Before using a held object with another object (e.g., a tool), first verify the held object's identity by using `examine <held-object>` if it is admissible. This prevents acting on incorrect assumptions about what you are holding.
- When you are at the target receptacle and hold the prepared object, immediately execute the available "move [object] to [receptacle]" action. Do not perform extra examinations or movements.
- If `go to <receptacle>` results in 'Nothing happens', immediately use `examine <receptacle>` to confirm its contents before moving elsewhere.

- **Direct transformation actions:** When at an appliance (microwave, stove, fridge) while holding an object that needs a state change (heat, cool, cook), scan admissible actions for a direct verb+object+appliance pattern (e.g., 'heat potato with microwave') before attempting manual placement. Use the direct action when available — do not open the appliance, place the object inside, or place it on the appliance; use the direct action while holding it.

- **Target not at destination → storage next:** If you arrive at the destination location and the target object is not visible among the listed objects, immediately navigate to the nearest storage container (drawer, cabinet, shelf) that could plausibly hold it. Do not exhaustively check other open surfaces first. Runtime check: after `go to` a destination, if the observation lists objects but the target is absent, your next action must be `go to` a storage container, not another open surface.


- **Closed-container confirmation:** When you open a closed container and it appears empty, confirm by scanning the post-open observation for any listed contents before moving on. Never assume a closed container is empty without opening it first — the observation after opening is authoritative.

- **HARD RULE — direct transformation only:** When holding a target object at an appliance (microwave, stove, fridge, sink), scan admissible actions for a direct verb+object+appliance pattern (e.g., 'heat tomato with microwave', 'cool potato with fridge'). If such an action exists, use it immediately. NEVER open the appliance, place the object inside, close it, or take it back out — the direct action handles everything in one step. Self-check: "Does the admissible list contain '<verb> <held_object> with <appliance>'? If yes, use it now and skip all manual open/place/close steps."
- **Verify held object before terminal actions:** When you arrive at a sink, shelf, or other destination with the intention to clean, place, or transform an object, use `inventory` first to confirm you are carrying the correct target object. Do not assume you are holding it — verify before executing the terminal action. Self-check: "Am I certain I am holding the target object?" If not, use `inventory` before any `clean`, `move`, or `put` action.
- **Pre-take container check:** Before executing any `take <object> from <container>`, verify in your action history that you have already opened that container. If not, open it first. Never assume a closed container's contents are accessible.
## Task-Type Procedures


### Goal-Adjective Transformations
When the goal specifies an adjective (e.g., "clean", "hot", "cooled"), the object must undergo a state change before being placed at the destination. Before heading to the final receptacle, navigate to the appliance that can achieve that state (sink for clean, stove for hot, fridge for cooled, etc.) and perform the corresponding action. Never move to the final receptacle before completing the transformation. Runtime check: while holding the target object, verify whether the goal adjective implies a transformation; if so, complete that transformation before moving to the final location.

When the goal contains "clean" before an object name (e.g., "put a clean butterknife in drawer"), locate a sinkbasin and use the action `clean <object> with sinkbasin` before delivering the object. Runtime check: "Does the task description contain the word 'clean'? If so, have I used a sink or cleaning appliance on the object before delivery?"



### Transformation-to-Delivery Cycle
When the goal requires a state change (heat, cool, clean, slice) and a target receptacle, execute this linear sequence without deviation:
1. Go to the target object
2. Take it
3. Go to the transformation appliance
4. At the appliance, scan admissible actions for a direct transformation action (e.g., `heat <object> with <appliance>`). If present, execute it immediately. Only if no direct action is available, open the appliance and place the object inside. Do not open the appliance unnecessarily.
4a. If the object is not in your inventory after the transformation (e.g., you placed it inside the appliance), **take it immediately** before proceeding.
5. Verify the held object's state matches the goal adjective (use `inventory` or the most recent observation; re-examine if unconfirmed)
6. Check if a direct 'move [object] to [receptacle]' action is admissible. If yes, execute it immediately; otherwise, go to the target receptacle and place the object.
Do not inspect other locations, examine held objects unnecessarily, or explore unrelated areas between steps 2 and 7.

Before each navigation step in this cycle, confirm it directly advances you toward the next subgoal (locate → take → transform → deliver). Do not detour.
### Device-Object Interaction


When the task requires using a device on another object (e.g., "examine X with Y" or "look at X under Y"), first locate and take the target object (X) into your inventory. Then navigate to the device (Y) and activate it. Do not activate the device before picking up the target object. This ensures you can immediately perform the final action with the object in hand.
### Device-Object Interaction
When the task specifies using a device on another object (e.g., "examine X with Y"), upon locating the device, activate it immediately (e.g., `use desklamp 1`) before leaving its location. If you already hold the other object, you can then use the device on it; if not, fetch the other object after activation. Do not leave the device location unactivated to get the other object first.
### Look-at-under-light Tasks
When the goal is to "look at X under the Y" (e.g., "look at alarmclock under the desklamp"), first navigate to X, take it, then navigate to Y and use Y. Do not activate the light before picking up the object. Runtime check: "If the task is 'look at OBJECT under LIGHT,' have I already taken OBJECT before I activate LIGHT?"

Before acting on any task, parse its phrase structure: "put a [transformed state] [object] in [destination]" implies (1) get [object], (2) apply [transformation], (3) deliver to [destination]. Verify your plan matches this sequence.

### Heat-and-Deliver Tasks

When the task is to heat an object and place it somewhere, follow this linear sequence without deviation:

1. Go to the likely storage location for the object (e.g., fridge for perishables, cabinet for non-perishables).
2. If the container is closed, open it.
3. Take the object.
4. Go to a heating appliance (microwave, stove, toaster).
5. Heat the object using a direct combined action if available (e.g., `heat potato with microwave`). If not, place and activate the appliance.
6. Go to the target receptacle.
7. Place the object on that receptacle.

Do not examine other items, do not revisit empty locations, and do not backtrack. Complete the sequence linearly.
## Common Pitfalls


- Do not add unnecessary examination steps (e.g., "look" or "examine") before picking up a target object that is already visible and reachable, and do not re-examine after discovery. If the object is listed and a "take" action is available, use it directly.
- Avoid blind sequential search: do not scan cabinets/drawers in order when the goal implies a likely location (e.g., fridge for perishable food). Use task semantics to prioritize. Exhaustively visiting every countertop and table before checking storage containers often wastes steps.
- Repeatedly cycling through already-inspected locations without new information is a common mistake; track visited locations and their contents to avoid this.
- **Unnecessary detours after acquiring target:** Once the target object is in hand, go directly to the goal location and complete the task. Do not inspect other items or explore unrelated areas.


- **Continuing after completion:** Once you execute the action that satisfies the task goal (e.g., moving the target object to the required receptacle), stop immediately. Do not re-examine, re-open, or re-handle objects. Ask: "Did I just complete the task?" and if yes, take no further actions.
- Do not use `inventory` or `examine` on a surface/location when its contents have already been explicitly described in a prior observation. The observation text is reliable. Only use these actions when they would provide genuinely new information (e.g., you just picked something up and need to verify what you're holding).
- **Revisiting exhausted locations:** Never return to a receptacle you have already inspected and found empty of the target object unless you have new information (e.g., you just placed or transformed something there). Before navigating to any location, confirm it has not already been visited and rejected as empty. Repeatedly cycling back to the same empty fridge, cabinet, or drawer wastes steps.



- **Landmark-first for prepositional goals:** When the task description contains a prepositional landmark (e.g., "under the desklamp", "inside the fridge"), locate and interact with the landmark BEFORE handling the target object. The landmark may need to be opened, turned on, or otherwise activated. Pause after reading the goal and identify the landmark phrase; if the landmark is not visible in the current observation, systematically visit candidate surfaces until it appears. Only after the landmark is located and any required action (e.g., "use desklamp 1") is performed should you handle the target object.
- **No action repetition without changed observation:** If an examine, look, or other action returns a generic/non-informative observation (e.g., "There's nothing special about…"), do NOT repeat that exact action on the same object or surface on the next step. Change context: move to a different location, examine a different object, or use a different admissible action. Before taking an action, verify it is not the identical action you took on the previous step unless the observation has meaningfully changed.

- **Re-examining on arrival (HARD RULE):** When you arrive at a location, the observation text already lists all visible items and container states (e.g., "On the desk 1, you see a pencil 1" or "On the sinkbasin 1, you see nothing"). This observation is authoritative. Do NOT use `examine` on that location — act on the arrival observation immediately (take an item, open a closed container, or go elsewhere). Only use `examine` when the arrival observation does NOT describe the receptacle's contents at all. Runtime check before any `examine`: "Did the arrival observation already tell me what's on/nothing is on this receptacle?" If yes, skip `examine` and decide your next navigation action immediately.

- **Skipping destination receptacles for storage:** When the task specifies a target receptacle type (e.g., stoveburners, desklamps, shelves), visit every instance of that receptacle type before opening any storage container. Survey all destination receptacles to check if the target object is already there and to identify which ones are empty. Only after exhausting all instances of the destination type should you search storage. Runtime check: "Have I visited every instance of the target receptacle type?" If not, do not open any cabinet, drawer, or other storage.

- **Fixating on one object while ignoring other required objects:** When the task involves using object A with object B (e.g., 'examine X with Y'), do not repeatedly interact with A alone if B has not been located. Instead, systematically search for B before attempting the final action. Runtime check: list all distinct objects named in the task instruction; if any are still unseen, go to an unexplored surface or container, not to interact with the objects you already have.

- When the task requires an object with a compound name (e.g., 'butterknife', 'desklamp'), treat any visible object whose base name matches (e.g., 'knife', 'lamp') as a potential target. If you see 'knife 1' in a drawer and the task asks for 'butterknife', take it and proceed — it is almost certainly the target. Do not ignore a matching object because the name is not an exact match.


- **Never return to a surface already searched and found empty.** If you visited desk 1, saw no target, then checked a drawer and found it empty, do NOT go back to desk 1 — you already know it's empty. Move to the next unvisited location instead. Before any `go to`, verify: "Have I already visually inspected this exact location and confirmed the target is absent?" If yes, skip it permanently.


- **Opening destination before holding target:** When the task requires placing an object into a receptacle, do NOT open or navigate to the destination receptacle until you are holding the target object in your inventory. First locate, take, and transform the object; only then identify and go to the destination. Runtime check before opening any receptacle: "Am I currently holding the target object?" If not, redirect to search.


- **Re-executing completed tasks:** After executing the final action that satisfies the task goal (e.g., moving the target object to the required receptacle), stop immediately. Do not pick up the object again, re-cool, re-heat, or re-place it. If the observation confirms the final placement, take no further actions. Self-check: "Did I just complete the task?" If yes, stop — do not interact with the target object again.

- **Fixating on initial object location in fixture tasks:** When the task requires using a fixture (e.g., desklamp) with an object you already hold, do NOT repeatedly return to the location where you found the object. If the fixture is not visible there, immediately begin a systematic sweep of every other unvisited location from the initial room observation. Never revisit the object's origin location until all other locations have been exhausted. Runtime check: "Have I visited every unexplored location from the initial observation since picking up the object?" If no, go to the next unvisited location now.

- **Track visited-and-empty locations explicitly:** Maintain a mental checklist of every receptacle you have visited and confirmed does NOT contain the target object. Before any `go to` action, consult this list: "Have I already been to [destination] and confirmed the target is absent?" If yes, pick a different, unvisited location from the admissible list. Never return to a location on this list unless you have new information (e.g., you just placed or transformed something there).

- **Unnecessary appliance opening:** When you arrive at an appliance holding the target object, check admissible actions for a direct transformation action (e.g., `heat X with microwave`) before opening the appliance. Using the direct action saves steps and prevents cycles. Do not open the appliance, place the object inside, and then retrieve it again.

- **Revisiting empty containers:** Before opening a closed container (drawer, cabinet, fridge), verify you haven't already opened it and found it empty. If you have, skip it permanently. Self-check: "Have I already opened this container and found it empty?"
- **Redundant examine on open containers:** If the observation after arriving at or opening a container already states its contents (e.g., "In it, you see nothing" or "In it, you see a book"), do NOT use `examine` on that container. The observation is authoritative. Only `examine` if the container's contents are ambiguous or not described.
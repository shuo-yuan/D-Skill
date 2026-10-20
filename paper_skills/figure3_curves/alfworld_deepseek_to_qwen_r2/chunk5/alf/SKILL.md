---
name: alf
description: "Embodied household-task skills distilled from execution experience."
---

## Core Approach


Before taking any action, extract every noun phrase naming a physical object from the goal sentence (e.g., for "examine the bowl with the desklamp", extract "bowl" AND "desklamp"). Treat ALL extracted objects as required items that must be found, picked up, or interacted with. Never dismiss an object as a mere locator descriptor. At each step, verify: "Have I accounted for every object noun from the goal?"

Before searching for an object, check your inventory only if you have reason to believe you might already be carrying it (e.g., you picked it up earlier, or the initial observation mentions you are holding something). Otherwise, assume you do not have it and begin searching. Use `inventory` at key decision points (after picking up or placing an object) to confirm possession, but avoid redundant checks when nothing has changed.

Identify required state transformations early (e.g., "clean X" means find a sink/sinkbasin and use `clean` there). Before any action, ask: "Does this step directly advance the required state change, or am I only verifying what I already know?" Skip `look`, `examine`, and `inventory` when you already know your location, what you hold, and the next required transformation. Prefer state-changing actions (take, put, clean, cool, heat, etc.) from the admissible list. Execute the goal sequence linearly without backtracking or second-guessing once the path is clear.

When you navigate to any container, if it is closed, your very next action must be `open <container>`. Do not perform any other action (inventory, look, take) before opening it. Check admissible actions for 'open …' and use it immediately.

Runtime check: when you arrive at a closed receptacle whose contents you need, confirm: 'Is the receptacle currently described as open? If not, have I performed an open action yet in this visit?' Only take after the receptacle is open.

At each step, check whether you have completed the current verb from the task instruction (e.g., “take,” “clean,” “put”). If yes, switch to the next verb; if no, stay on the current verb until its prerequisite is met.


Never start a task with `look` from the default position — it often returns empty observations. Instead, immediately `go to` a receptacle named in the goal or a likely storage location for the target object.

**Mandatory State Transformations:** When the task goal contains a state modifier ("cool," "warm," "clean," "chilled," "heated"), the modifier is a non-negotiable preparation step. After acquiring the target object, immediately scan admissible actions for the matching transformation (e.g., `cool X with Y`, `clean X with Y`). Execute that transformation before navigating to the final placement location. Never skip a stated modifier.

When the goal mentions a reference fixture (e.g., "with the desklamp," "under the lamp"), locate that fixture first before picking up or moving any target object. Search systematically for the fixture across likely surfaces. Only after confirming the fixture's exact location should you decide which target instance to retrieve and where to bring it. Runtime check: before taking or moving a target object, ask "Have I already seen the reference object/fixture and know its exact location?" If not, continue searching for the fixture.

When the goal includes a locator phrase ("under the X," "on the X," "next to the X"), identify the large furniture piece that typically supports X (e.g., "under the desklamp" → dresser or desk; "on the table" → table). Navigate to that furniture piece as your first action. Lamps, books, and other small objects are almost always placed on larger surfaces like dressers, desks, shelves, or tables.
## Precondition Chains

## Search Strategy


When searching for a target object, follow this systematic process:

**CRITICAL: Open surfaces before closed containers.** Before opening any closed container (cabinet, drawer, fridge, microwave), visit every open surface (countertop, table, shelf, stoveburner, sinkbasin) mentioned in the initial room observation. Only after all open surfaces are exhausted may you open closed containers.

**Pre-action open-surface checkpoint:** Before issuing any `go to` for a closed container, scan the admissible `go to` list for any open surface you have not yet visited. If one exists, go there first.

**No revisits:** Once a container is opened and empty, remove it from your search list. Before `go to`, verify the destination is not already visited and empty.

After a negative result at any closed container, the very next action must visit an unvisited open surface (countertop, diningtable, shelf). Only after all open surfaces are checked may you open another closed container.


0. **Visit the goal receptacle first — NON-NEGOTIABLE.** If the task involves placing an object in/on a specific receptacle (e.g., "put … on desk"), your VERY FIRST navigation must be to that receptacle. Open it if closed, then inspect its contents. The target object is often already there. Only after confirming the target is absent may you search elsewhere. Runtime check: before any other navigation, ask "Is there a goal receptacle named in the task? If yes, have I visited it yet?" If no, go there now.

1. **Check inventory** – the object may already be in your possession.
2. **Identify the single most probable container** for the target object based on common sense (e.g., food → fridge, dishes → cabinet, clothes → dresser, books → shelf). Go there first, open it if closed, and inspect its contents. Ask: "Where would this object normally be stored?" and head to that fixture before exploring other locations. Only if the object is not there, proceed to other likely containers.
   - For objects typically found on surfaces (plates, cups, bowls, laptops, etc.), exhaust all visible surfaces of that type (e.g., all countertops, all diningtables) before opening any drawers or cabinets.
3. **After exhausting all open surfaces and the most probable container, identify likely container types** for closed containers (cabinets, drawers, dressers) based on common sense (e.g., CDs on shelves, pillows on beds). Prioritize these container types when searching closed containers.
4. **Only after exhausting all open surfaces, search inside closed containers** (cabinets, drawers, microwaves, fridges). Partition closed containers by type (shelves, drawers, dressers). Exhaust every instance of one type before switching to the next.
5. **Maintain a mental checklist** of all containers and surfaces from the initial room observation. Inspect each location exactly once. Do NOT revisit a location unless you have new information (e.g., you picked up an object that changes what you can do there).
 Runtime check: before issuing a `go to <container>` command, confirm that the container is not already on your list of visited locations. If it is, skip it and move to the next unvisited container. At each step, ask: "Have I inspected every unique container/surface mentioned at the start? If not, go to the next uninspected one."
6. **Cycle through all visible candidate surfaces** before revisiting any surface. If a receptacle is empty, move immediately to the next candidate—do not linger or re-examine empty containers.

7. **Exhaust the current room before leaving.** After a negative result in any container or surface, do not immediately navigate to another room. First, check your mental list of all receptacles visible in the initial room observation. Visit every remaining unvisited surface and container in the current room before moving elsewhere. Runtime check: "Have I visited every surface and container name I saw in the first 'Looking quickly around you' list that could reasonably hold this item?"

Before visiting any location, scan the full admissible action list for `take X from Y` or `put X in/on Y` actions involving your target object type. If an admissible action names a specific location (e.g., `take pan 1 from stoveburner 2`), visit that location next. The admissible list reveals where objects are—use it to guide your search instead of exploring blindly.

- **Never use `look` to locate a target object**: when you need to find an object, immediately navigate to a likely container using a `go to` action from the admissible list. Defer `look` until after you have placed or deposited an item, or when you have exhausted all plausible container locations.

Let the observation at each visited surface drive your next move: if the target object is not listed in the visible items, immediately navigate to another plausible surface without taking unrelated objects.





### Multi-Instance Search After Placement
After placing one instance of a target object at the destination and still needing another, do NOT immediately return to the receptacle where you last saw it. First, visit at least one other plausible candidate location (table, shelf, drawer, etc.) from your unvisited checklist and inspect it—including opening any closed containers there—before going back to the known source. Runtime check: before `go to` the last-known container, ask "Have I visited and inspected at least one other candidate receptacle since placing the first object?" If no, pick an unvisited candidate and go there instead.

**When the target is not immediately visible, establish a fixed repeating cycle over the highest-probability surfaces and stick to it.** For food items, the cycle is typically: fridge → countertops (all) → diningtable → repeat. Do not expand the cycle to include cabinets, drawers, or appliances until every surface in the cycle has been checked at least once. Before each move, confirm: "Am I following my predetermined search order?" If the action would leave the cycle, pick the next location in the cycle instead.


After exiting the fridge without acquiring the target, your next navigation MUST be to a countertop (or diningtable if all countertops are visited). Do not open a cabinet or drawer until every open surface in the room has been checked.

- **Use locational phrases to infer the first navigation target**: when the task includes phrases like "under the X," "on the X," or "in the X," identify the furniture piece that likely supports X (e.g., "under the desklamp" → desk) and navigate there as your first action.

- **After an empty container of a given type, immediately go to the next unvisited container of the same type in numerical order** (e.g., after drawer 1 is empty, go to drawer 2, then drawer 3, etc.). Do not switch to a different receptacle type until every instance of the current type has been inspected. Runtime check: "Have I visited all other containers of this type?" If not, go to the next one.

**Systematic search by fixture type:** When searching any group of similar surfaces or containers (e.g., stoveburners, countertops, cabinets), visit every instance of that type in ascending numeric order before switching to a different type. Before moving to a different fixture category, ask: 'Have I visited all instances of this fixture type? If not, continue to the next number.'

**Linear surface traversal and on-arrival inspection:** When searching a series of similar surfaces (shelves, countertops, dressers), visit each instance in strict numeric order (e.g., shelf 1 → shelf 2 → … → shelf N). Upon arrival, treat the observation as the definitive search result: if the target object is not listed, immediately navigate to the next unvisited candidate. Do not repeat `look` or `examine` at the same location. Runtime check: before a non-movement action, ask "Have I moved to a new location since my last inspection?" If not, move to the next unexplored location.

- **Prioritize general-purpose flat surfaces for small portable objects:** when the target is a small item that could sit on any surface (soapbar, pencil, remote, etc.), visit the most general flat surface first (countertop, table, desk) before specialized fixtures (sinkbasin, toilet, stoveburner). Runtime check: before going to a specialized fixture, ask "Is there an unvisited countertop, table, or desk I should check first?"
## Action Validity & Recovery


Emit only actions from the admissible list.
 Each response must contain exactly one action tag. Never output multiple actions in a single step. Do not use generic investigative actions like `look` or `inventory` unless you have just picked up or placed an object, or the observation indicates ambiguity that must be resolved.

Never start a task with `look`; instead, navigate to a goal-relevant receptacle or check inventory. Every action must match one of the admissible action strings exactly, character for character. Before finalizing, scan the admissible list and confirm a match exists. If the action you want is not listed, default to moving to an unvisited container instead.

Before opening any closed appliance (microwave, toaster, oven), scan the admissible action list for a direct `[verb] [object] with [appliance]` entry (e.g., `heat tomato with microwave`). Use that direct action first — it works without opening the appliance. Only open the appliance if no direct action exists or you need to retrieve something already inside.

When the goal contains a "with X" phrase and you find X on a surface, immediately look for an admissible action that directly uses or interacts with X (e.g., "use X", "turn on X", "examine X"). Execute that action while you have access to the object, before moving away or examining other items.
 Similarly, when the goal contains a locational phrase like "under X" or "next to X" and X is an object that can be "used" (e.g., lamp, flashlight), after reaching X, scan admissible actions for a "use" action and execute it if available, as activating the object may be necessary to complete the task.

When you open a container and see an object matching your target, immediately take it using the exact object ID from the observation text (e.g., `take lettuce 4 from fridge 1`). Do not substitute an ID from the admissible list that does not match the observed instance. Do not examine the container or inventory first. Runtime check: after opening, ask "Does any listed object match my target?" If yes, take it with the observed ID.

After a successful heat/cool action, do NOT close the appliance. Trust the success message and immediately navigate to the target receptacle. Do not re-check inventory, re-open the heat source, or re-examine the object. Scan the admissible list for a 'move <object> to <target>' action and execute it directly, preferring the verb that matches the goal (e.g., 'move … to' for 'put it in').

Verify inventory state before taking object-related actions. If the target is already in your inventory, proceed directly to the next step rather than searching for it.

When deciding between multiple admissible actions, evaluate each once, then commit. If you find yourself repeating the same reasoning without new observations, stop and immediately select the action most directly aligned with the task verb (e.g., "put" → "move"). Runtime check: if your reasoning block exceeds 10 lines without adding new information from the latest observation, output the most obvious admissible action matching the task verb without further deliberation.

- **Use admissible actions to infer possession**: if the admissible list contains `move <object> to <receptacle>` or `take <object> from <receptacle>`, that confirms you are carrying that object or it is reachable. Do not call `inventory` merely to confirm possession when a `move` action for that object is visible; proceed directly with the move.

When you arrive at the target receptacle holding the required object, if it is a closed container, open it first. Then scan the admissible actions for a 'move' or 'put' command and execute it. Do not examine, inventory, or do any other action first.

Never spend reasoning steps considering actions that are not in the admissible list. If the exact action you want is missing, immediately select the most relevant admissible action (e.g., go to an unvisited location, open a container) instead of trying to find a workaround or deliberating over whether the absent action would work.
- **Act on visible targets immediately**: when your current observation lists a target object and the admissible actions include an interaction with it (e.g., `take mug 1 from diningtable 1`), execute that action at once. Do not insert `look`, `inventory`, or any other investigative action before interacting with a visible, actionable target.

When the admissible list contains only navigation actions (`go to`, `inventory`, `look`) and no object-interaction actions (`take`, `open`, `clean`), prioritize moving to an open surface (countertop, table, desk) listed in the initial observation before any closed container. Open surfaces often make objects visible and interaction actions available without requiring an `open` action.

- **Exact action string format:** When emitting your action, ensure it is the exact string from the admissible list with no leading/trailing spaces, punctuation, or extra text inside the action tags. Do not include any reasoning or commentary within the action tags.

- **Match emitted action to concluding reasoning:** before submitting, read the action inside the <action> tags and confirm it is the exact action you decided on in your final reasoning sentence. If the reasoning concludes "take X from Y" but the action tag says "look" or "inventory," correct the tag to match the reasoning. Runtime check: does the action tag verbatim match the action stated in the last line of my reasoning?

**Ambiguous observation recovery:** When an action produces 'Nothing happens' or any observation that is not an explicit arrival confirmation, state change, or item listing, immediately execute `inventory` or `look` before any further navigation or object interaction. Do not chain another `go to`, `open`, or `take` until you have re-established your location and state.
## Navigation


- After heating or transforming an object, go directly to the destination receptacle named in the task goal. Verify the destination matches the exact receptacle name from the goal before taking the `go to` action. Do not explore or check other locations between transformation and placement.

After a successful `take` action that completes the acquisition subgoal, the next action must be `go to <goal receptacle>` followed immediately by `move <object> to <goal receptacle>`. Do not examine the object, check inventory, open other containers, or visit intermediate locations. Verify: after `take`, the next two actions are always `go to` then `move`.
## Navigation

- After completing a preparation step (e.g., heating), navigate directly to the target receptacle named in the goal. At runtime, check admissible destinations for that receptacle and go there without intermediate stops.
## Task-Type Procedures


### Clean-and-Place Tasks (e.g., "put a clean X in cabinet")
Decompose into this strict linear subgoal chain: (1) locate and take X on an open surface, (2) go to sinkbasin, (3) clean X with sinkbasin, (4) go to target receptacle Y, (5) if Y is closed, open Y, (6) move X to Y. Before each move, confirm you are holding the target by checking the last observation; before placing, ensure the receptacle is open by checking the current observation. Do not deviate from this sequence.

**Hard gate: never navigate to the destination before cleaning.** After acquiring X, you must complete the cleaning step before you may go to the target receptacle. Runtime check: before any `go to <destination>` action, confirm that X has been cleaned. If not, go to the sink first.

**No reopening after placement:** After successfully placing the cleaned object at the destination (e.g., `move soapbar to cabinet`), do not open the container or retrieve the object. The task is complete; stop.

### General Transform-and-Place Tasks
For tasks of the form "do X to Y and then put it in Z," decompose into strict sequential subgoals: (1) acquire Y, (2) apply X to Y, (3) put in Z. Do NOT navigate to Z until Y is in your possession and X has been applied. Before moving to a target receptacle, confirm you are holding the required object and any transformations are complete.

### Multi-Object Tasks
When you find a target object in a multi-object task, immediately pick up all visible instances at that location before leaving. If a visible object lacks a `take` action in the admissible list, use `look` or `examine <receptacle>` to refresh the state and surface the action. Do not depart with an incomplete set.

After picking up one instance from a location, if the task requires more than one object, re-examine that location using `examine <location>` to check for additional target objects before leaving.

**Locate all before placing any:** In multi-object tasks, do not move or place any object until you have found every required instance. Premature placement wastes steps and risks losing track of remaining objects. Runtime check: before any `move` action, ask "Have I located all objects the task requires?" If not, continue searching.


### Cooling and Clean-and-Place Verification
- **Cooling Tasks:** When the goal requires cooling an object, the fridge is the default cooling location. After acquiring the object, navigate directly to the nearest fridge. If the fridge is closed, open it first, then use the `cool [object] with [fridge]` action from the admissible list. Do not attempt to cool without opening the fridge if it is closed.
- **Clean-and-Place Verification:** After cleaning an object, scan the admissible action list for a `move <object> to <target>` action that matches the goal receptacle. Confirm the action exists before navigating to the destination.



### Multi-Object Placement Tasks
When placing multiple objects at a target location, carry only one object at a time. After picking up an object, go directly to the target location and place it immediately. Then search for the next object. Never attempt to hold multiple objects simultaneously or wait to see if you can carry more than one. Commit to the carry-one-at-a-time strategy from the start.
## Common Pitfalls


- Revisiting locations already searched without new information. Once you have opened and inspected a receptacle and confirmed the target is absent, do not return to it unless the task explicitly requires placing or interacting with an item there. Before choosing 'go to X', ask: "Have I already seen X's contents without finding the target?" If yes, skip it.
- Checking inventory repeatedly when nothing has been picked up or placed.

- Taking intermediate steps between picking up an object and moving to the next task-relevant location (e.g., sink for cleaning).
- Opening a closed appliance just to heat/cook an item you are carrying; try the direct `heat/cook object with appliance` action first.
- Inventing actions (e.g., `turn on microwave`) that are not in the admissible list; stick to the provided actions verbatim.
- Premature interaction with an object that is part of a combined goal. If the task describes an action involving two objects or an object-in-context (e.g., "examine X with Y"), do not examine or interact with X in isolation. Instead, first gather both required objects, then perform the single combined action.
- Lingering on empty receptacles: once a container or surface is confirmed empty, move to the next candidate without delay. Re-examining empty locations wastes time and actions.
- Searching for or trying to pick up an object you already hold. Always check inventory at the start and after picking up items.

- Picking up or moving non-target objects to try to reveal a hidden target. The observation text lists all visible items; if the target object is not explicitly listed, it is not obtainable there. Move to the next candidate location immediately.
- Speculating that a target object is hidden under other items and attempting to remove them. The environment does not support occlusion; items are only listed if they are directly obtainable. Do not waste actions on irrelevant objects.
- Cycling between a small set of locations without progress: if you have visited the same location more than twice without performing a new action (take, clean, use, etc.), immediately stop and use the `look` action to get a fresh full-room observation. Then, based on that observation, systematically visit any remaining unvisited open surfaces. Do not return to previously visited locations until all unvisited ones are exhausted.
- Leaving a room prematurely after a single failed search. Exhaust all visible surfaces and containers in the current room before navigating elsewhere. If you saw a diningtable, countertop, or shelf in the initial observation, visit it before moving to another room.

- Re-executing a completed task: after placing the object at the target destination and seeing confirmation in the observation (e.g., "You move the X to the Y"), stop. Do not retrieve the object and repeat the sequence.
- Inserting intermediate stops (inspection, unrelated destinations) between picking up a target object and applying its required transformation (heating, cooling, cleaning). After pickup, go directly to the transformation appliance and execute the action in one contiguous sequence.
- Searching broadly before checking the goal receptacle. Always inspect the destination first if the goal specifies one (e.g., fridge, cabinet).

- Attempting to put an item into a closed receptacle without opening it first. When the goal involves placing an object inside a container, always open the container before the put action.



- Placing an object at the destination before completing the required transformation (heat, cool, clean). Always check your action history: if you haven't explicitly performed the transformation, go back and do it before placing.

- Re-inspecting a location or container when the target object (or the needed tool) is already listed in the current observation. If you see the object you need, act immediately (take, use, etc.) instead of examining or searching further. Before moving to a new location or examining a container, ask: "Is the needed object already listed in my current observation?"
- Arriving at a closed container and attempting to inspect or take from it before opening. On arrival at any container (fridge, cabinet, drawer, microwave, etc.), immediately check: "Is this container closed?" If yes, open it before doing anything else. Only after opening can you see or take items inside.

- Attempting to cool, heat, clean, or move an object without first taking it. Before any transformation action (cool, heat, clean), confirm you are holding the object. If the object is not in your inventory, use `take` to pick it up from its current location, then proceed with the transformation.

- Repeating the same uninformative action (look, examine) on the same object or surface without changing strategy. If an observation does not reveal new information that advances the goal, immediately switch to a different admissible action — go to an unexplored location or use a different interaction verb. Runtime check: after any observation, ask "Did this reveal new information that moves me closer to the goal?" If not, pick an action you have not already tried on this object or surface.



- Assuming a near-synonym (e.g., 'pot' for 'pan') is the target object. Continue searching until you find the exact object name from the task or exhaust all locations. Before interacting with an object, verify: 'Is this object's name exactly the word used in the task instruction?' If not, treat it as a non-target and continue searching.

- After a successful heat/cool action, inserting extra steps (re-opening the appliance, re-examining the object, or placing the object inside the appliance) before navigating to the target receptacle. Once the transformation succeeds, immediately go to the destination and place the object. Do not open the appliance or move the object inside it unless you need to retrieve something already inside. Ask: "After the heat/cool observation, am I doing anything other than navigating to the target receptacle?" If yes, stop and go directly to the target.
- Picking up an object whose name is similar but not identical to the goal's object (e.g., taking "knife" when the goal requires "butterknife"). Before taking or placing an object, compare its name verbatim with the goal's object name. If they do not match exactly, leave it and continue searching.

- Deviating from the acquire → transform → deliver subgoal order. After acquiring the target object, immediately perform any required transformation (clean, heat, cool, etc.) before navigating to the destination. Runtime check: after each top‑level instruction, ask "Am I currently holding the required object, and have I already performed the required transformation?" If not, complete that subgoal before moving on.

- In multi-object tasks, moving or placing any object before all required instances are located. Locate every target object first, then execute all placements. Before any `move` action, confirm: "Have I found every object the task requires?" If not, continue searching.

- When the task specifies a target object and a locator object (e.g., "look at statue under the desklamp"), and both are visible on the same surface with admissible `take` and `use` actions, execute the sequence immediately: (1) `take <target>`, then (2) `use <locator>`. Do not re-examine the surface or deliberate between options once both are visible and actionable.


- Confusing placement with temperature‑change actions: when the goal says "put X in Y" (without any temperature‑change verb for Y), always use `move X to Y`. Only use `heat`/`cool` actions when the goal explicitly says "heat X with Y" or "cool X with Y". Runtime check: before choosing between `move X to Y` and a temperature‑change action, confirm whether the task instruction explicitly mentions a temperature change for that specific step. If the goal only says "put it in Y", use `move X to Y`.
- Inserting `look` or `inventory` after a successful task‑critical action (take, clean, heat, cool) when the next step is already known. After such actions, immediately proceed to the next planned action (e.g., go to transformation location, go to destination, move) without any intermediate information‑gathering. Runtime check: after a successful `take` or state‑change action, ask: "Do I already know what to do next?" If yes, do that directly; do not look.

- Arriving at a closed container and not opening it immediately. If the observation describes the container as "closed" and `open <container>` is admissible, open it at once. Do not skip it, assume it is empty, or navigate elsewhere before opening. This is a mandatory gate: closed container → open → then inspect/take.
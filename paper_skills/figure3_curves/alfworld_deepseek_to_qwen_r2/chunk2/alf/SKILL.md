---
name: alf
description: "Embodied household-task skills distilled from execution experience."
---

## Core Approach


Before taking any action, extract every noun phrase naming a physical object from the goal sentence (e.g., for "examine the bowl with the desklamp", extract "bowl" AND "desklamp"). Treat ALL extracted objects as required items that must be found, picked up, or interacted with. Never dismiss an object as a mere locator descriptor. At each step, verify: "Have I accounted for every object noun from the goal?"

Before searching for an object, check your inventory only if you have reason to believe you might already be carrying it (e.g., you picked it up earlier, or the initial observation mentions you are holding something). Otherwise, assume you do not have it and begin searching. Use `inventory` at key decision points (after picking up or placing an object) to confirm possession, but avoid redundant checks when nothing has changed.

Identify required state transformations early (e.g., "clean X" means find a sink/sinkbasin and use `clean` there). Before any action, ask: "Does this step directly advance the required state change, or am I only verifying what I already know?" Skip `look`, `examine`, and `inventory` when you already know your location, what you hold, and the next required transformation. Prefer state-changing actions (take, put, clean, cool, heat, etc.) from the admissible list. Execute the goal sequence linearly without backtracking or second-guessing once the path is clear.

When you navigate to any container, if it is closed, your very next action must be `open <container>`. Do not perform any other action (inventory, look, take) before opening it. Check admissible actions for 'open …' and use it immediately.

At each step, check whether you have completed the current verb from the task instruction (e.g., “take,” “clean,” “put”). If yes, switch to the next verb; if no, stay on the current verb until its prerequisite is met.
## Precondition Chains

## Search Strategy


When searching for a target object, follow this systematic process:

0. **Visit the goal receptacle first** – if the goal involves placing an object in/on a specific receptacle (e.g., "put … in fridge"), go directly to that receptacle, open it if needed, and inspect its contents. The target object is often already there, saving search effort. Only proceed to broad search if the object is not found there.

1. **Check inventory** – the object may already be in your possession.
2. **Identify likely container types** based on common sense (e.g., CDs on shelves or dressers, not inside garbage cans; pillows on beds, lamps on desks). Prioritize these containers in your search.
3. **Search all open surfaces** (countertops, stoveburners, sinkbasin) where objects are immediately visible. At each surface, if the target object is listed, take it immediately. If not, move on. At runtime, ask: "Have I inspected every location whose name appears in the current observation with visible items?" Move on immediately if the target is absent.
4. **Only after exhausting all open surfaces, search inside closed containers** (cabinets, drawers, microwaves, fridges). Partition closed containers by type (shelves, drawers, dressers). Exhaust every instance of one type before switching to the next.
5. **Maintain a mental checklist** of all containers and surfaces from the initial room observation. Inspect each location exactly once. Do NOT revisit a location unless you have new information (e.g., you picked up an object that changes what you can do there).
 Runtime check: before issuing a `go to <container>` command, confirm that the container is not already on your list of visited locations. If it is, skip it and move to the next unvisited container. At each step, ask: "Have I inspected every unique container/surface mentioned at the start? If not, go to the next uninspected one."
6. **Cycle through all visible candidate surfaces** before revisiting any surface. If a receptacle is empty, move immediately to the next candidate—do not linger or re-examine empty containers.

7. **Exhaust the current room before leaving.** After a negative result in any container or surface, do not immediately navigate to another room. First, check your mental list of all receptacles visible in the initial room observation. Visit every remaining unvisited surface and container in the current room before moving elsewhere. Runtime check: "Have I visited every surface and container name I saw in the first 'Looking quickly around you' list that could reasonably hold this item?"

Before visiting any location, scan the full admissible action list for `take X from Y` or `put X in/on Y` actions involving your target object type. If an admissible action names a specific location (e.g., `take pan 1 from stoveburner 2`), visit that location next. The admissible list reveals where objects are—use it to guide your search instead of exploring blindly.

- **Never use `look` to locate a target object**: when you need to find an object, immediately navigate to a likely container using a `go to` action from the admissible list. Defer `look` until after you have placed or deposited an item, or when you have exhausted all plausible container locations.

Let the observation at each visited surface drive your next move: if the target object is not listed in the visible items, immediately navigate to another plausible surface without taking unrelated objects.
## Action Validity & Recovery


Emit only actions from the admissible list. Do not use generic investigative actions like `look` or `inventory` unless you have just picked up or placed an object, or the observation indicates ambiguity that must be resolved.

Never start a task with `look`; instead, navigate to a goal-relevant receptacle or check inventory. Every action must match one of the admissible action strings exactly, character for character. Before finalizing, scan the admissible list and confirm a match exists. If the action you want is not listed, default to moving to an unvisited container instead.

Before opening any closed appliance (microwave, toaster, oven), scan the admissible action list for a direct `[verb] [object] with [appliance]` entry (e.g., `heat tomato with microwave`). Use that direct action first — it works without opening the appliance. Only open the appliance if no direct action exists or you need to retrieve something already inside.

When the goal contains a "with X" phrase and you find X on a surface, immediately look for an admissible action that directly uses or interacts with X (e.g., "use X", "turn on X", "examine X"). Execute that action while you have access to the object, before moving away or examining other items.

When you open a container and see an object matching your target, immediately take it using the exact object ID from the observation text (e.g., `take lettuce 4 from fridge 1`). Do not substitute an ID from the admissible list that does not match the observed instance. Do not examine the container or inventory first. Runtime check: after opening, ask "Does any listed object match my target?" If yes, take it with the observed ID.

After a successful heat/cool action, do NOT close the appliance. Trust the success message and immediately navigate to the target receptacle. Do not re-check inventory, re-open the heat source, or re-examine the object. Scan the admissible list for a 'move <object> to <target>' action and execute it directly, preferring the verb that matches the goal (e.g., 'move … to' for 'put it in').

Verify inventory state before taking object-related actions. If the target is already in your inventory, proceed directly to the next step rather than searching for it.

When deciding between multiple admissible actions, evaluate each once, then commit. If you find yourself repeating the same reasoning without new observations, stop and immediately select the action most directly aligned with the task verb (e.g., "put" → "move"). Runtime check: if your reasoning block exceeds 10 lines without adding new information from the latest observation, output the most obvious admissible action matching the task verb without further deliberation.

- **Use admissible actions to infer possession**: if the admissible list contains `move <object> to <receptacle>` or `take <object> from <receptacle>`, that confirms you are carrying that object or it is reachable. Do not call `inventory` merely to confirm possession when a `move` action for that object is visible; proceed directly with the move.

When you arrive at the target receptacle holding the required object, immediately scan the admissible actions for a 'move' or 'put' command and execute it. Do not examine, inventory, or do any other action first.
## Navigation


- After heating or transforming an object, go directly to the destination receptacle named in the task goal. Verify the destination matches the exact receptacle name from the goal before taking the `go to` action. Do not explore or check other locations between transformation and placement.
## Navigation

- After completing a preparation step (e.g., heating), navigate directly to the target receptacle named in the goal. At runtime, check admissible destinations for that receptacle and go there without intermediate stops.
## Task-Type Procedures


### Clean-and-Place Tasks (e.g., "put a clean X in cabinet")
Decompose into three ordered subgoals:
1. Acquire X (locate and take it).
2. Clean X using an available basin/sink.
3. Place X in/on Y.

At the start of the task, explicitly list these phases and ensure every action serves exactly one of them. Follow a direct sequence: after acquiring the object, immediately go to the sink, clean the object, then go to the target receptacle and place it. Avoid detours.

### General Transform-and-Place Tasks
For tasks of the form "do X to Y and then put it in Z," decompose into strict sequential subgoals: (1) acquire Y, (2) apply X to Y, (3) put in Z. Do NOT navigate to Z until Y is in your possession and X has been applied. Before moving to a target receptacle, confirm you are holding the required object and any transformations are complete.

### Multi-Object Tasks
When you find a target object in a multi-object task, immediately pick up all visible instances at that location before leaving. If a visible object lacks a `take` action in the admissible list, use `look` or `examine <receptacle>` to refresh the state and surface the action. Do not depart with an incomplete set.

After picking up one instance from a location, if the task requires more than one object, re-examine that location using `examine <location>` to check for additional target objects before leaving.


### Cooling and Clean-and-Place Verification
- **Cooling Tasks:** When the goal requires cooling an object, the fridge is the default cooling location. After acquiring the object, navigate directly to the nearest fridge and use the `cool [object] with [fridge]` action from the admissible list. Do not open the fridge first — the direct `cool … with …` action works without opening.
- **Clean-and-Place Verification:** After cleaning an object, scan the admissible action list for a `move <object> to <target>` action that matches the goal receptacle. Confirm the action exists before navigating to the destination.
## Common Pitfalls


- Revisiting locations already searched without new information. Once you have opened and inspected a receptacle and confirmed the target is absent, do not return to it unless the task explicitly requires placing or interacting with an item there. Before choosing 'go to X', ask: "Have I already seen X's contents without finding the target?" If yes, skip it.
- Checking inventory repeatedly when nothing has been picked up or placed.
- Opening containers before exhausting all open surfaces.
- Taking intermediate steps between picking up an object and moving to the next task-relevant location (e.g., sink for cleaning).
- Opening a closed appliance just to heat/cook an item you are carrying; try the direct `heat/cook object with appliance` action first.
- Inventing actions (e.g., `turn on microwave`) that are not in the admissible list; stick to the provided actions verbatim.
- Premature interaction with an object that is part of a combined goal. If the task describes an action involving two objects or an object-in-context (e.g., "examine X with Y"), do not examine or interact with X in isolation. Instead, first gather both required objects, then perform the single combined action.
- Lingering on empty receptacles: once a container or surface is confirmed empty, move to the next candidate without delay. Re-examining empty locations wastes time and actions.
- Searching for or trying to pick up an object you already hold. Always check inventory at the start and after picking up items.

- Picking up or moving non-target objects to try to reveal a hidden target. The observation text lists all visible items; if the target object is not explicitly listed, it is not obtainable there. Move to the next candidate location immediately.
- Speculating that a target object is hidden under other items and attempting to remove them. The environment does not support occlusion; items are only listed if they are directly obtainable. Do not waste actions on irrelevant objects.
- Cycling between a small set of locations without progress: if you have visited the same location more than twice without performing a new action (take, clean, use, etc.), immediately redirect to an unvisited location from the initial room observation. Do not return to previously visited locations until all unvisited ones are exhausted.
- Leaving a room prematurely after a single failed search. Exhaust all visible surfaces and containers in the current room before navigating elsewhere. If you saw a diningtable, countertop, or shelf in the initial observation, visit it before moving to another room.

- Re-executing a completed task: after placing the object at the target destination and seeing confirmation in the observation (e.g., "You move the X to the Y"), stop. Do not retrieve the object and repeat the sequence.
- Inserting intermediate stops (inspection, unrelated destinations) between picking up a target object and applying its required transformation (heating, cooling, cleaning). After pickup, go directly to the transformation appliance and execute the action in one contiguous sequence.
- Searching broadly before checking the goal receptacle. Always inspect the destination first if the goal specifies one (e.g., fridge, cabinet).

- Attempting to put an item into a closed receptacle without opening it first. When the goal involves placing an object inside a container, always open the container before the put action.
---
name: alf
description: "Embodied household-task skills distilled from execution experience."
---

## Core Approach


Before taking any action, extract every noun phrase naming a physical object from the goal sentence (e.g., for "examine the bowl with the desklamp", extract "bowl" AND "desklamp"). Treat ALL extracted objects as required items that must be found, picked up, or interacted with. Never dismiss an object as a mere locator descriptor. At each step, verify: "Have I accounted for every object noun from the goal?"

Before searching for or interacting with any object, check your inventory first. Use the `inventory` action at key decision points to confirm whether you already possess the target object. This prevents redundant searching and wasted actions.

Identify required state transformations early (e.g., "clean X" means find a sink/sinkbasin and use `clean` there). Before any action, ask: "Does this step directly advance the required state change, or am I only verifying what I already know?" Skip `look`, `examine`, and `inventory` when you already know your location, what you hold, and the next required transformation. Prefer state-changing actions (take, put, clean, cool, heat, etc.) from the admissible list. Execute the goal sequence linearly without backtracking or second-guessing once the path is clear.

When you arrive at a closed container relevant to the goal, open it immediately as your next action. Do not navigate away to explore other locations first. Check admissible actions for 'open …' and use it before moving elsewhere.
## Precondition Chains

## Search Strategy


When searching for a target object, follow this systematic process:

1. **Check inventory** – the object may already be in your possession.
2. **Identify likely container types** based on common sense (e.g., CDs on shelves or dressers, not inside garbage cans; pillows on beds, lamps on desks). Prioritize these containers in your search.
3. **Search all open surfaces** (countertops, stoveburners, sinkbasin) where objects are immediately visible without opening anything. At runtime, ask: "Have I inspected every location whose name appears in the current observation with visible items?" Move on immediately if the target is absent.
4. **Only after exhausting all open surfaces, search inside closed containers** (cabinets, drawers, microwaves, fridges). Partition closed containers by type (shelves, drawers, dressers). Exhaust every instance of one type before switching to the next.
5. **Maintain a mental checklist** of all containers and surfaces from the initial room observation. Inspect each location exactly once. Do NOT revisit a location unless you have new information (e.g., you picked up an object that changes what you can do there). At each step, ask: "Have I inspected every unique container/surface mentioned at the start? If not, go to the next uninspected one."
6. **Cycle through all visible candidate surfaces** before revisiting any surface. If a receptacle is empty, move immediately to the next candidate—do not linger or re-examine empty containers.
## Action Validity & Recovery


Emit only actions from the admissible list. Do not use generic investigative actions like `look` or `inventory` unless you have just picked up or placed an object, or the observation indicates ambiguity that must be resolved. Every action must match one of the admissible action strings exactly, character for character. Before finalizing, scan the admissible list and confirm a match exists. If the action you want is not listed, default to moving to an unvisited container instead.

Before opening any closed appliance (microwave, toaster, oven), scan the admissible action list for a direct `[verb] [object] with [appliance]` entry (e.g., `heat tomato with microwave`). Use that direct action first — it works without opening the appliance. Only open the appliance if no direct action exists or you need to retrieve something already inside.

When the goal contains a "with X" phrase and you find X on a surface, immediately look for an admissible action that directly uses or interacts with X (e.g., "use X", "turn on X", "examine X"). Execute that action while you have access to the object, before moving away or examining other items.

When you open a container and see an object matching your target, immediately take it with the first matching `take` action. Do not examine the container or inventory first. Runtime check: after opening, ask "Does any listed object match my target?" If yes, take it.

After heating an object, scan the admissible list for 'move <object> to <target>' to complete the task. Prefer the verb that matches the goal verb (e.g., 'move … to' for 'put it in').

Verify inventory state before taking object-related actions. If the target is already in your inventory, proceed directly to the next step rather than searching for it.

## Navigation

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
## Common Pitfalls


- Revisiting locations already searched without new information.
- Checking inventory repeatedly when nothing has been picked up or placed.
- Opening containers before exhausting all open surfaces.
- Taking intermediate steps between picking up an object and moving to the next task-relevant location (e.g., sink for cleaning).
- Opening a closed appliance just to heat/cook an item you are carrying; try the direct `heat/cook object with appliance` action first.
- Inventing actions (e.g., `turn on microwave`) that are not in the admissible list; stick to the provided actions verbatim.
- Premature interaction with an object that is part of a combined goal. If the task describes an action involving two objects or an object-in-context (e.g., "examine X with Y"), do not examine or interact with X in isolation. Instead, first gather both required objects, then perform the single combined action.
- Lingering on empty receptacles: once a container or surface is confirmed empty, move to the next candidate without delay. Re-examining empty locations wastes time and actions.
- Searching for or trying to pick up an object you already hold. Always check inventory at the start and after picking up items.
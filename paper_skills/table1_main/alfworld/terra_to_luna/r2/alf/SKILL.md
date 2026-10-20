---
name: alf
description: "Embodied household-task skills distilled from execution experience."
---

## Core Approach


Prefer the shortest action sequence that accomplishes the task. Avoid unnecessary examinations or inventory checks once the required objects and locations are identified.
Maintain explicit awareness of the full task goal at each step; before acting, recall the overall objective and the next subgoal.

Ignore all objects not explicitly mentioned in the task goal. Before taking or using any object, verify that it appears in the task instruction. If it does not, do not interact with it; continue searching or moving.

When the admissible actions include a composite command that accomplishes a subgoal in one step (e.g., `clean <object> with <fixture>`, `heat <object> with <appliance>`, `cool <object> with <appliance>`), use it immediately instead of performing intermediate steps like moving the object to the fixture first.
## Precondition Chains

## Search Strategy


When searching for a target object, follow these rules:
- **Open surfaces first**: Exhaust all visible open surfaces (countertops, shelves, tables, sinkbasin, bathtubbasin) before opening any closed container. At each step, ask: "Are there unseen open surfaces in this view?" If yes, visit the next one and examine its contents.
- **Semantic first location**: Before your first movement, identify the target object from the task goal. Scan the initial observation for all open surfaces and ask: "Which open surface is most likely to contain this object?" (e.g., cd → desk, book → shelf, plate → diningtable). Go to that surface first, even if it is not the lowest-numbered surface. After checking it, proceed to the remaining open surfaces in ascending numerical order.
- **Numbered open surfaces**: If the open surfaces are numbered (e.g., countertop 1, countertop 2), after checking the most likely surface (if any), visit the remaining surfaces in ascending numerical order without skipping any. This ensures all visible open surfaces are checked before moving to closed containers.
- **Systematic container order**: After open surfaces are exhausted, open closed containers in a systematic order: exhaust all instances of one type (e.g., all drawers, then all cabinets) before switching to a different type.
- **All container types**: After exhausting one container type, move to the next distinct container type from the initial scene description (e.g., dresser, desk, sidetable, garbagecan) and exhaust all instances of that type. Do not skip any container type that can hold objects.
- **Track inspected locations**: Maintain a mental list of every container and surface already examined. Before moving to a location, ask: "Have I already inspected this location and found it empty?" If yes, skip it. Never revisit a location (surface or container) you have already fully inspected unless the task requires placing an item there or new information suggests an object may have appeared. If an observation explicitly says "you see nothing", do not return to that location later for searching. Maintain a single forward pass through all receptacles; after each action, quickly name the next three unchecked containers in your planned sequence.
- **Exhaust initial containers**: From the very first observation, list every container mentioned. Visit each at least once before revisiting any previously checked container. After each navigation step, confirm no initial container remains unvisited; if any are left, go to one of them next.
- **Target receptacle after open surfaces for put tasks**: For any task that requires placing objects into a specific container or container type, first check all open surfaces for the target object. Only after all open surfaces have been checked and the object is not found, go to the target receptacle. This ensures you don't waste time opening closed containers when the object is in plain sight. After reading the goal, ask: “Have I checked every open surface for the object?” If not, visit them first.
- **Open closed containers immediately**: When you arrive at a closed container (drawer, cabinet, etc.), open it immediately before moving on or doing anything else. This ensures hidden objects are not overlooked.
If you are in a location with multiple closed containers, open and inspect each one before moving to another location.

- **Numbered containers**: When encountering numbered containers (e.g., drawer 1, drawer 2, cabinet 1, cabinet 2), visit them in ascending numerical order, opening and examining each one even if earlier ones are empty. Do not stop until all instances of that type are exhausted. Never return to a container with a lower number; before moving, recall the highest number already inspected and only go to a strictly larger number. Before leaving a container category, confirm you have opened every numbered instance.
- **Runtime check before opening containers**: Before opening any cabinet, drawer, or closed appliance (fridge, microwave), verify that you have visited every open surface (countertop, shelf, table, sinkbasin, bathtubbasin) in the current environment and confirmed the target is absent. If any open surface remains unvisited, go there first.
- **Open-surface scan before opening**: Before navigating to or opening any closed container, scan the admissible `go to` actions for any open surface (countertop, diningtable, sidetable, etc.) that you have not yet visited. Go there first. This check applies even if you believe the object is likely inside a closed container.

- **Immediate target check**: After opening a closed container or arriving at a surface, immediately scan the observation for the target object name. If the target is absent, move directly to the next unvisited candidate location from the initial scene description without any extra actions (e.g., closing, examining, inventory checks).
- **Functional priors**: If the target object is strongly associated with a specific fixture (e.g., dishsponge → sinkbasin, apple → fridge, pot → stoveburner), navigate to that fixture first, before checking other locations. If the object is not there, then check all open surfaces before opening other closed containers. For all fruits, vegetables, and dairy products, the fridge is the strongly associated fixture; go there first, even if the final destination is elsewhere. Ask: 'Where would this object most likely be?' and go there next.
- **Appliance first for cooling/heating tasks**: For any task that requires cooling or heating an object, go to the appliance (fridge for cool, microwave/stove for heat) as your first action, because the object is likely stored there. If the object is not inside, then check open surfaces before other closed containers.


- **Explicit open-surface list**: At the start of any search, list all open surfaces visible in the scene (countertops, tables, shelves, etc.) and plan to visit each one before opening any closed container.
- **Checklist from initial observation**: Before your first action, copy every receptacle (surface or container) mentioned in the initial observation into a checklist. Mark each as unchecked. As you visit a location, mark it as done. Never visit a location already marked done unless you need to place an object there or new information (e.g., a key) makes it relevant. After each navigation step, verify the next location is still unchecked; if it is already done, pick the next unchecked location from the checklist instead.
- **Pre-navigation check**: Before issuing any `go to` command, confirm that the destination is not a location you have already inspected and found empty (for containers, ask: 'Have I already opened and inspected this container?'). If it is, pick the next unvisited location from your checklist instead.
- **Pre-search destination check**: In any put task, before opening a container or examining a surface to find the target object, confirm that you have already navigated to the destination receptacle and observed that the object is not there. If you have not, go to the destination first.
- **After a failed closed-container search**: If you open a closed container (fridge, cabinet, drawer) and the target is not inside, immediately check all open surfaces (countertops, tables, desks, sinks) in the current room before opening another closed container. Ask: "Have I inspected every visible countertop/surface here?" If not, visit and inspect each one next.
- **Immediate placement for multi-object tasks**: When the task requires placing multiple identical objects into a target, after picking up one object, go directly to the target receptacle and place it before searching for the next object. Never take a second object before completing the first placement. Runtime check: after a successful `take` on a goal object, your next action should be `go to <target>` (unless already there) followed by `move ... to <target>`.

- **Loop prevention**: After every 5 actions, review the admissible 'go to ...' options and choose a location you haven't visited yet. If all known locations have been visited, open a closed container at any of them. This prevents revisiting the same spot repeatedly.
- **Exact match first**: Search for an object whose name exactly matches the target word. Only after all locations are exhausted and no exact match appears may you consider a close variant (e.g., 'knife' for 'butterknife', 'sponge' for 'dishsponge'). Do not pick up a differently named object (e.g., 'cup' for 'mug') unless it is an obvious substring or synonym and you have exhausted all other options. Before picking up any object, compare its lowercase name to the target object word in the task description; if they are not identical, leave it and continue searching.

- **Admissible action check**: Before taking an object, verify that the object name in the admissible `take` command exactly matches the target object word. If it does not (e.g., `take pan` when the goal is `pot`), skip that action and continue searching.

- **Empty-container surface check**: After opening a closed container and not finding the target, check all unvisited open surfaces before opening another closed container. Never open more than two closed containers in a row without checking open surfaces in between.

- **Systematic exhaustive search**: When searching for a specific object that is not visible, systematically visit every reachable location (all 'go to' options) at least once before revisiting any location. After each move, ask: 'Have I visited all reachable locations at least once?' Only revisit a location if all have been visited and the object is still not found.
- **First-move from initial observation**: After reading the task, scan the initial room observation for the target object or its typical container. If a promising location is listed among admissible `go to` actions, navigate there first. This leverages the scene description to avoid unnecessary searching.
- **Strong-association exception**: For objects with a strong functional association to a specific closed container (e.g., perishable food in fridge, dishsponge at sinkbasin, cooking items on stove), navigate directly to that container before checking open surfaces. If the object is not found there, then check open surfaces and other containers.
- **Container-name matching**: If the target object's name contains a container word (e.g., desklamp includes desk), and that container appears in the initial room observation, navigate directly to that container first, even if it is closed, before checking open surfaces.

- **Explicit surface listing after closed-container failure**: After opening a closed container (fridge, cabinet, drawer) and not finding the target, list every open surface mentioned in the initial observation (e.g., countertop 1, countertop 2, diningtable 1) and visit each one in order before opening any other closed container. Do not skip any surface, even if it seems less likely to contain the object.
## Action Validity & Recovery


- **Open closed containers**: If an observation states a container is 'closed' and `open` appears in the admissible actions, your next action must be the corresponding `open` command. Never attempt to take from, inspect, or place an object into a closed container without opening it first.
- **Skip examine when contents are known**: If the observation already describes the contents of the current location (e.g., 'In it, you see ...', 'On the ..., you see ...', or 'you see nothing'), do not use `examine` on that location; proceed directly to the next action.
- **Open before leaving**: Before moving away from a closed container, check admissible actions: if `open` is present, use it first, because objects may be hidden inside.
- **Location verification**: Before any `open`, `take`, or `examine` action, ensure you are at the correct container or surface. Verify that your current location (the "You arrive at…" line) matches the object's location mentioned in the action.

- **Avoid unnecessary inventory checks**: Only use `inventory` when you have just picked up or put down an object, or need to confirm the identity/state of a held object before acting on it. During the search phase, if you haven't taken any object, your inventory is empty; rely on observations of surfaces and containers instead.
- **Immediate open rule**: If `open <container>` appears in the admissible actions after arriving at a container, first confirm that you have visited every open surface (countertop, table, shelf, sidetable, coffeetable, etc.) listed in the initial room observation. If any open surface remains unvisited, navigate there first. Only if all open surfaces have been exhausted, execute the `open` command immediately. Do not examine or look around first; opening directly reveals contents.


- **Verify possession before critical actions**: After picking up an object, use `inventory` to confirm it is in hand. Before any `clean`, `heat`, `cool`, or `put` action, check inventory again; if not holding the correct item, backtrack to the object's location and take it.

- **Runtime check for closed containers**: After arriving at a receptacle, if the observation says it is closed, confirm that your next action is the corresponding `open` command. Do not examine or take from it before opening.

- **Runtime check before examine**: Before using `examine` on a surface or container, recall the last observation about it. If it was already reported as empty (e.g., 'you see nothing'), do not examine it; instead, proceed to the next unvisited location.
## Task-Type Procedures


### Put tasks
When the goal is to put objects into a target container, go to that container first. Observe its contents. If the object is not present, then leave to search nearby containers. **Runtime check:** After arriving at the destination and before leaving to search, read the observation and confirm that the object is not in its surface inventory.
Note the objects currently at the destination; when you later return to place the target object, confirm it is not already occupied by a different instance of the same object type.

**After picking up the object:** Once you are carrying the target object, navigate to the destination receptacle and use the appropriate move/put action. Runtime check: if your inventory contains the object and the admissible actions include a move to the required destination, choose it immediately.


**Upon arrival at the target receptacle:** When you are holding the required object and have just arrived at the target receptacle, scan admissible actions for the `move` command and execute it immediately. Do not examine the receptacle or the object unless the move action is missing.

- **Location confirmation**: After arriving at the destination receptacle, verify that the observation text includes the receptacle name (e.g., 'You arrive at drawer 2'). If it does not, navigate to the correct receptacle before placing.

**Runtime check after take:** After successfully taking the target object, confirm that your next action navigates directly to the goal destination (e.g., `go to <destination>`). Do not examine or move the object to an intermediate location.
### Cooling/Heating Tasks
- After picking up the target object, navigate directly to the required appliance (fridge for cool, microwave/stove for heat).
- Once at the appliance, immediately look for the `cool <object> with <appliance>` or `heat <object> with <appliance>` action in the admissible actions list.
- Execute the action without first examining or opening the appliance, unless the required action is missing from the list.

- **Runtime check**: When you are at the required appliance (fridge for cooling, stove/microwave for heating) holding the target object, scan admissible actions for the appropriate transformation action (e.g., 'heat ... with stove', 'cool ... with fridge'). If it is present, execute it immediately. Do not open the appliance, place the object inside, or close the appliance unless the required action is missing.
- After executing the heat or cool action, read the observation to confirm the transformation succeeded (e.g., 'You heat the apple', 'You cool the apple'). If the transformation message is absent, repeat the action. Once confirmed, navigate straight to the target receptacle, open it if it is closed, and place the object inside (e.g., `move ... to ...`). Do not deviate; confirm the target receptacle immediately after the transformation.

- **Pre-heating verification**: Before heating or cooling an object, go to the target receptacle and check admissible actions. If you do not see an action like `put <object> in <receptacle>` or `place <object> on <receptacle>`, do not heat/cool the object. Instead, re-examine whether you have the correct object or whether the correct object exists elsewhere. This prevents wasting steps on an incorrect object.
- **Never manually open the appliance and move the object inside if a composite heat/cool action is available.** The composite action performs all necessary preparation in a single step.
- **Runtime check:** Before selecting `open <appliance>` or `move <item> to <appliance>`, scan the admissible actions for any `heat/cook/warm … with …` action; if present, use it immediately.


- **Early fridge access**: When the task involves cooling an object, go to the fridge and open it as one of your very first actions—even before you have the item. This lets you check if the target is already there. Runtime check: *Is cooling part of my goal? Have I opened the fridge yet?* If not, make that a priority.


- **Runtime check after transformation**: Once the heat/cool action succeeds and the object is ready, immediately issue `go to <target receptacle>`. Do not stop to examine other objects, open other containers, or check inventory. The only acceptable next action is navigation to the destination specified in the task goal.
### Pick, Clean, and Place / Put a clean X in Y
Follow this sequence: (0) go to the target receptacle Y first and inspect its contents; if X is already there, take it and proceed directly to cleaning (step 3); otherwise, (1) locate and take X, (2) go to a cleaning location (sinkbasin, bathtub, etc.), (3) clean X, (4) go to Y, (5) put X in/on Y. Before each action, verify your current state matches the next step. After cleaning, scan admissible actions for a `move ... to <target receptacle>` entry; if missing, you are not at the correct receptacle; go there before placing.
- **Open-surface priority**: When searching for X, check all open surfaces before opening any closed containers.

Once you have the target object, proceed directly to the cleaning location without stopping at other containers or surfaces.
Runtime check: After taking the target object, confirm that your next action is a `go to` command to the cleaning location. Do not examine the object or any other items; proceed immediately. After cleaning, go directly to the target receptacle.

Runtime check: When you arrive at the cleaning location, scan admissible actions for a 'clean <object> with <fixture>' command. If present, execute it immediately without examining the fixture or the object first.

### Tool-Use Tasks
For tasks that require using a tool on an object (e.g., "examine X with Y"), follow this pattern:
1. Identify the likely surface(s) for the object and the tool from the initial scene description.
2. Go to the first plausible surface for the object.
3. If the object is not there, immediately go to the next candidate surface without examining the empty surface.
4. Once you find and take the object, go directly to the tool's surface.
**After taking the object:** Immediately check inventory to confirm you have it, then scan admissible actions for a `go to` command that leads to the tool's surface and execute it. Do not deviate.
5. Use the tool immediately (e.g., `use desklamp on pillow`). Do not examine the tool or the object unless the use action is missing.
**Runtime check:** Before each action, ask: *Does this action get me closer to having the target object in hand or to activating the target tool with the object in hand?* If the answer is no, prefer a direct `go to`, `take`, or `use`.

After picking up the target object, do NOT examine it; go directly to the tool's surface. If you examine the target and get a neutral result (e.g., "nothing special"), that is a signal the tool is missing; immediately stop examining and search for the tool. **Runtime check:** Before any `examine <target>`, confirm the tool is in hand or at the current location. If not, find the tool first.

When searching for the tool, prioritize open surfaces (shelves, tables) across all furniture pieces before opening drawers or cabinets. Do not open drawers of the same furniture piece while other open surfaces remain unexplored. Maintain a checklist of all furniture/containers from the initial room description; visit each once before revisiting any.

For "look at X under Y" tasks where Y is a light source (e.g., desklamp, floorlamp), treat Y as a tool that requires X in hand. Always retrieve X from a typical location (bed, shelf, table) first, then go to Y and use Y on X. **Runtime check:** If you are at Y and do not hold X, never activate the light; instead, leave and search for X.
## Common Pitfalls


Missing transformation adjectives: After picking up a target object, reread the task instruction. If it contains adjectives like 'clean', 'cold', 'hot', 'cooked', etc., perform the corresponding transformation (e.g., `clean ... with sinkbasin`, `cook ... with microwave`) at the appropriate appliance before placing the object. After picking up the object, explicitly verify: state the adjective from the task and confirm whether you have executed the transformation.
- **Pre-placement checkpoint**: Before executing a `move` or `put` action to place the object, re-read the task goal and confirm that any required transformation (cool, heat, clean, etc.) has been performed. If not, go to the appropriate appliance first.


- **Examining the destination before placing**: When you are at the target receptacle and carrying the object to be placed, do not examine the receptacle or interact with other items. If the admissible actions contain a `move <object> to <receptacle>` command, execute it immediately.

- **Prepositional phrases as fixtures**: If the task says "look at X under/on/in Y", Y is a separate fixture that must be located and operated (e.g., `use Y`). After picking up X, navigate to Y's location and interact with it. Do not treat Y as a mere location descriptor. **Runtime check**: If you have X and `examine X` does not complete the task, scan admissible actions for interactions with Y; if none, navigate to furniture pieces that could hold Y until Y appears and becomes usable.
- **Starting with closed containers**: Never begin a search by going to a drawer, cabinet, or other closed container if any open surface (countertop, shelf, table, sinkbasin, bathtubbasin) is reachable. Always visit open surfaces first. Even if a drawer or cabinet appears first in the list of admissible go-to locations, ignore it and go to an open surface instead.
- **Examining a closed container instead of opening**: If a container is closed and the admissible actions include `open`, use `open` directly. Examining a closed container only confirms it is closed and wastes a turn.

- **Premature examination of target without required tool**: In tool-use tasks, do not examine the target object until you have the tool and are ready to use it. If you get a neutral result, treat it as a signal to find the tool. Before any `examine <target>`, verify the tool is in hand or at the current location; if not, locate the tool first.
- **Avoid idle object movement**: Once you pick up an object needed for the task, keep it in your inventory. Do not move it to another surface unless that surface is the final destination. Before any 'move X to Y' action, ask: 'Is Y the goal location?' If not, do not move it.

- **Collecting cleaning tools unnecessarily**: For clean tasks, go directly to a sink (sinkbasin) and use the `clean X with sinkbasin` action. Do not pick up dishsponges, cloths, or soap bottles; they are not required. Only if the admissible actions at the sink do not include a clean action should you consider using a tool.

- **Activating a light source without the target object**: In 'look at X under Y' tasks, never turn on or use the light source (Y) unless you are holding X. Before any light-activation command, check inventory; if X is not held, navigate to X's location and take it first.

- **Revisiting empty closed containers**: After opening a closed container and confirming the target object is not inside, do not return to that container during the search phase. The only exception is when you need to use that container for a task step (e.g., cooling in the fridge). Before any `go to` command, recall whether you have already opened that container and found it empty; if yes, skip it.
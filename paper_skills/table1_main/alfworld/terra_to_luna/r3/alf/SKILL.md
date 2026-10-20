---
name: alf
description: "Embodied household-task skills distilled from execution experience."
---

## First Action Rule

**CRITICAL:** When the task requires finding an object, your very first navigation action must be to an open surface (countertop, table, desk, shelf, etc.) listed in the initial observation. Never go to a closed drawer, cabinet, or fridge as your first action.
 This applies even if you expect the object to be in a drawer (e.g., utensils like spoons, forks) — check open surfaces first. This rule overrides all other considerations, including target receptacle visits. Only after all open surfaces have been inspected should you consider closed containers.

**Exception for put tasks:** If the task requires placing an object into a specific receptacle (e.g., 'put X in Y'), go to Y first, even if it is a closed container, because the target is often stored there. Open it if closed and check inside. If the target is not there, then search for X following the surface-first rule.


**Runtime check:** Before your first action, explicitly ask: "Are there any open surfaces (countertop, table, shelf, etc.) among the initial location list? If yes, I will inspect them before I go to any closed container."


**Appliance clue:** If the task instruction mentions a specific appliance or furniture (e.g., 'desklamp', 'floorlamp'), go directly to the open surface most likely to contain that appliance (e.g., desk for desklamp) as your first action, before inspecting other open surfaces. The target object is often co-located with its associated appliance.
## Core Approach


Plan the shortest sequence that directly achieves the goal. Decompose tasks into ordered sub-goals: locate the target object, apply any required transformation (e.g., cool, heat, clean), and deliver it to the destination. For retrieval-and-placement tasks, follow this pattern: (1) go to the target location, (2) search a nearby container, (3) take the object, (4) return to the target, (5) place it. Choose actions only from the current admissible-actions list and skip any step not strictly required—do not examine objects or locations unless the outcome depends on it.

When you arrive at a container and the observation says it is "closed", use the "open" action if it appears in your admissible actions to check inside. Never assume a closed container is empty.


Before taking any action, follow these priority rules:

- Prioritize searching open surfaces (tables, countertops, etc.) over closed containers. Before opening any drawer or cabinet, ensure you have inspected every open surface listed in the initial observation.
- If the task requires a specific object or tool that you do not currently have in your inventory, stop all other interactions and begin a systematic search for that missing item. Do not manipulate other objects; focus solely on locating the required item. Runtime check: before any action, ask: "Do I currently have the tool or object required by the task? If not, which locations have I not yet visited?"


- If the initial room observation explicitly lists a surface containing the target object (e.g., "On the desk 1, you see an alarmclock"), navigate there directly as your first action. If the target object is semantically associated with a specific open surface (e.g., cd with desk, plate with table), prioritize going to that surface first, even without explicit listing.
- After acquiring the target object and completing any required transformation, go directly to the destination and place it. Do not examine other locations or objects along the way. This applies to all task types: once the object is ready, the next action must move you toward the final placement.
- **No-transformation deposit:** If the task does not require cleaning, heating, or cooling, after picking up the target object, go directly to the destination receptacle. Open it if closed, then place the object inside. Do not stop at any other location.

- When beginning a search, consider the most likely storage location based on item type: perishable foods in the fridge, common dishware on open surfaces, tools in drawers, etc. Use the specific rules in Search Strategy to guide your first action.


- **Runtime check:** before each action, explicitly state which subgoal you are currently pursuing (e.g., 'acquire X', 'heat X', 'deliver X') and verify the action advances that subgoal.
## Precondition Chains


- If the task goal mentions a “clean” object (e.g., “put a clean butterknife in the drawer”), locate a sinkbasin and execute `clean <object> with sinkbasin` before moving the object to its final location. Before any `move` action that completes the task, verify that the `clean` step has already been performed for the target object.
- Before moving an object into a receptacle, verify the receptacle is open. If the observation describes it as "closed," execute `open <receptacle>` first.

- Before executing any `move <object> to <receptacle>` action, verify the latest observation says the receptacle is open. If it says it is closed or does not mention its state, issue `open <receptacle>` first.
## Search Strategy


**Systematic exploration (two-phase sweep):** When you enter a room, list every distinct location from the initial observation. Phase 1: Visit every open surface in a fixed order. Phase 2: Open and inspect every closed container in a fixed order. Do not stop after the first location that contains an object matching the target description; verify that you have checked all candidate locations.
During Phase 2, do not return to open surfaces; they were already inspected in Phase 1. Continue through all containers of one type without interruption.

**Surface-first rule:** Before you open any cabinet, drawer, or other closed storage, verify that you have visited every open surface (countertop, table, desk, shelf) mentioned in the room observation. If any surface remains unchecked, go there next. Only after all surfaces are exhausted may you start opening cabinets. Maintain a mental record of inspected locations. Prioritize open surfaces (countertops, tables, desks, etc.)—visit every open surface mentioned in the initial observation before searching any enclosed storage (cabinets, drawers). After all open surfaces have been inspected, search enclosed storage in a fixed order (e.g., numerically sorted cabinets, then drawers).

**Mandatory first search action:** When you first enter a room to search for an object, go to the first open surface (countertop, table, desk, etc.) listed in the observation. Do not go to any cabinet, drawer, or closed container until you have visited every open surface. Search one complete container type before switching to the next; never return to a container type you have already fully searched.

**Container inspection:** Open every closed container and inspect its contents before moving on. Do not skip a closed container that could hold target objects.
- When you arrive at a closed container, immediately open it; do not attempt to deduce its contents from the outside. Only after opening can you assess whether it holds the target.

**Examine avoidance:** Only use `examine` when the observation does not already list the visible contents (e.g., the container is closed or obscured). If the observation already states what is inside/on a container, accept that information and act on it.

**Ignore non-target objects:** Before taking any object, ask: "Is this the target object or a required tool for the very next step?" If not, move on immediately to avoid inventory clutter and wasted actions.



**Runtime checks:**
- After visiting a location, mark it as “checked”.
- Before moving to a new location, ask: “Have I already visited this location in the current search phase?” If yes, skip it and go to an unvisited location instead.
- Before opening any closed container (cabinet, drawer, fridge), confirm you have already looked on all visible surfaces.

- Do not revisit a location that was empty (or lacked the target object) until you have visited every other accessible location at least once. After exhausting all locations, you may revisit only if you have new information.


- **Common dishware and food items:** If the target is a plate, bowl, cup, fork, spoon, knife, or similar common dishware/utensils, or a loose, uncooled food item (e.g., tomato, apple, bread), verify that you have visited every open surface (countertops, tables, desks) before opening any storage. At each surface, read the listed objects; if the target is there, pick it up immediately. These items are rarely stored inside closed containers.
- **After opening a container:** If the observation lists its contents and the target object is not among them, immediately navigate to the next unvisited candidate location. Do not examine or take any object from that container.
- **Closed receptacle check:** Upon arriving at any receptacle (cabinet, drawer, fridge, etc.), if the observation says it is closed, your next action must be `open <receptacle>`. Do not use `examine` on a closed receptacle; open it immediately. Only consider `examine` after opening if the contents are not fully visible. Do not skip to another location until it is opened.
- **CRITICAL: Never revisit a receptacle you have already opened and inspected until you have exhausted all other unvisited receptacles.** Keep a running list of visited locations in your reasoning (e.g., 'visited: cabinet 1, cabinet 2, drawer 1') to avoid accidental revisits.
- After each movement, ask: “Have I visited all furniture types visible at the start that could hold the target?” If not, go to an unvisited type next.
- Before moving to a location, scan your observation history for the phrase "You arrive at" followed by that location name. If you see a previous arrival, skip it and move to the next unvisited location.
- Before taking any `open` action, confirm that you have visited all open surfaces (countertops, tables, sinkbasins, stoveburners) in the current room. If any remain unvisited, go to an unvisited open surface instead of opening a container.

- **Goal-object filter:** When an object list appears, ask: "Is this object an exact noun match for the goal object?" If not, skip it entirely—do not pick up, examine, or interact with it. (e.g., if the goal is 'mug', do not take 'cup'.)
- **Perishable foods:** If the target is a perishable food item (egg, milk, butter, etc.), go directly to the fridge first, open it, and check inside before searching any open surfaces. **Exception:** In put tasks, always go to the target receptacle first, even for perishable foods. The target receptacle may contain the object. After checking the target receptacle, if the object is not found, then proceed to the fridge.


- **Admissible-go-to marking:** At each decision point, look at the admissible `go to` actions and mentally mark those you have already inspected and found empty. Choose an unmarked location. If no unmarked locations remain, only then consider revisiting a location with a specific reason (e.g., to use an appliance).
- When moving to a container (cabinet, drawer, fridge), verify it is the next in your planned numerical order (e.g., cabinet 1, then cabinet 2, etc.) and that you have not already opened it in the current search.
- After each location visit, ask: “Have I visited every open surface in this room? Have I opened and inspected every closed container?” If the answer is no, continue the sweep before interacting with any found objects.


- **Open-surface priority before/after containers:** Before selecting a `go to` action to any cabinet, drawer, or fridge, confirm you have already visited every open surface (countertop, table, desk, etc.) in the room. After opening a closed container and not finding the target, if any open surface remains unvisited, go there next before opening another closed container.
- Before each `go to` action, consult your visited-locations list. If the location is in the list and was empty, skip it and choose an unvisited location.
- After picking up a target object that must be used with another item (e.g., a light source, a tool), systematically visit every furniture item in the room until you find that item. Do not examine the same surface or object repeatedly.


- **Checklist from admissible actions:** At the start of a room search, list every `go to` location from the admissible actions in your reasoning. As you visit each, mark it as checked. Do not revisit any checked location until all have been checked. This ensures you cover every receptacle exactly once before any revisit.
- **Before each `go to` action, explicitly ask: 'Have I already visited this location and found it empty?' If yes, skip it and choose an unvisited location.**



**Admissible take-action shortcut:** Before moving to a new location to search, scan the admissible actions for any `take <object> from <receptacle>` entry where `<object>` matches the target category (e.g., pot, pan, mug). If found, navigate directly to that receptacle and take the object, bypassing the systematic sweep. This reveals the object's location without opening closed containers.


- **Explicit surface checklist:** When you first enter a room, write down the names of every open surface from the initial observation (e.g., countertop 1, countertop 2, diningtable 1). Then visit each one in order, checking it off as you go. Do not skip any surface, even if you think it unlikely to hold the target. Only after all listed open surfaces are checked should you open any cabinet or drawer.


- **Task wording check:** Before moving to a location, if the task instruction mentions a specific appliance or furniture, verify that the location is the one most associated with that appliance. If not, reconsider whether a more direct route exists.
## Action Validity & Recovery


- Only use `examine X` when the observation does not already list the visible contents (e.g., X is closed or obscured). If the observation already states what is inside/on a container, accept that information and act on it.
- Before issuing any action, verify that the exact action string appears verbatim in the current "Your admissible actions" block and that you are holding the object you intend to use. Never guess, paraphrase, or construct an action outside that list.


- Use `inventory` only at the start of the task and after taking an object. Do not use `inventory` when you have not interacted with objects since the last inventory check, unless you have a specific reason to believe your inventory state has changed (e.g., you just placed an object or are unsure).
- Before using `examine`, verify that the current observation does not already describe the contents of the target. If the observation says "On the X, you see nothing" or lists items, do not examine; instead, act on that information.



- After picking up the target object (or completing a transformation), check: "Am I immediately moving to the goal location?" If the next action is not `go to <destination>`, stop and redirect to the destination.

- Before taking any object, confirm that the current observation text explicitly lists that object at your current location. If the observation does not mention the object, do not attempt to take it—navigate to where it is visible first.
## Task-Type Procedures


### Put Tasks



For put tasks (e.g., 'put X in Y'):
1. Go to the target receptacle Y and open it if closed. This prepares the destination.
2. Then search for the target object X using the surface-first rule.
3. Once X is in inventory, go directly to Y (if not already there) and place it.
4. If more instances of X are needed, resume searching from the next unvisited location in your mental checklist; do not revisit previously searched containers.



**CRITICAL:** In put tasks, the very first action must be to go to the target receptacle Y, even if the object is commonly found elsewhere (e.g., fridge). This rule overrides any other search heuristics, including the perishable food rule. After arriving at Y, if the object is not found, search all open surfaces in the room before opening any closed containers.


**Runtime check:** After picking up X, confirm your next action is `go to <destination>` and that the destination name exactly matches the task's target receptacle (e.g., `coffeetable 1` for "put statue on coffeetable").
### Clean-Object Tasks
For tasks involving a “clean” object (e.g., “put a clean X in Y”), follow this sequence:
1. Locate and pick up X first from typical storage spots (countertops, cabinets, drawers). Do not go to the sink until you are actually holding X and need to clean it. At the start, before moving, ask: “Have I picked up X yet?” If not, your immediate goal is to search surfaces and containers—not the sink.
2. Once holding X, go to a sinkbasin and execute `clean <X> with sinkbasin` (or similar cleaning station) to clean the object.
3. Then go to the target receptacle and place it using a `move` action.
Before any `move` action that completes the task, verify that the `clean` step has already been performed for the target object.


**Runtime check:** After picking up a target object that needs cleaning, confirm the next two actions are: (1) go to a cleaning-capable fixture, (2) clean the object with that fixture. Only after that should you navigate to the destination receptacle.

If you do not yet have the object after reaching the target receptacle, search for it by following the surface-first rule: visit all open surfaces in the room before opening any closed containers.


**Runtime check:** After executing `clean <X> with sinkbasin`, verify the observation contains a message like "You clean the X using the sinkbasin." Only then proceed to the target receptacle.



**Tool warning:** Do not collect any cleaning tool (e.g., dishsponge, cloth) unless the admissible actions at the sink require it. The `clean` action typically works with just the object and the sinkbasin. Before picking up any item for cleaning, go to the sinkbasin and check the admissible actions. If `clean <X> with sinkbasin` is present, do not fetch any tool.
### Examine with Tool Tasks
When the task instruction contains the word "with" (e.g., "examine X with Y"), treat Y as a required tool, not an optional location hint. Follow this sequence:
1. Locate and pick up Y first from typical storage spots. Do not interact with X until Y is in your inventory.
2. Once holding Y, go to X and execute the examine action (e.g., `examine X with Y`).
3. Do not consider examining X alone as a valid completion step; the task is only satisfied when the action with Y is performed.

**Runtime check:** If the task phrase contains "with [object]", pause and check your inventory and current location for that object. If it is absent, search for it before interacting further with the first object.


**Stationary tool exception:** If the tool Y is a stationary fixture (e.g., desklamp, sink, stove), reverse the order: first locate and pick up X, then go to Y and execute the examine action. Before using the tool, confirm you are holding X. Runtime check: before executing the examine action, verify that you are holding the target object X; if not, retrieve it first.

**After picking up X (stationary tool):** Do not examine X alone. Immediately navigate to Y and use it. If Y is a light source (desklamp, floorlamp), the correct action is `use <Y>` while holding X.

**Tool search check:** When searching for Y after picking up X, only go to furniture you have not yet visited. Before each move, confirm the location is not in your visited list to avoid re-inspecting empty spots.
### Look at X under Y Tasks
When the task is phrased as "look at <object> under <light>" (or similar with other light sources), treat it as a procedure:
1. Locate and pick up any instance of the target object first from typical spots. Do not waste steps checking whether the object is already under the light; assume it is not.
2. Once holding the object, go to the light source (e.g., desklamp, floorlamp). If the light source is on a furniture item, navigate to that furniture.
3. Use the light source while holding the object (e.g., `use desklamp` or `examine <object> with <light>`). Do not place the object down first.
**Runtime check:** Before examining an object or surface to see if it is already "under" something, stop and instead plan: "Which object do I need? Where is the light source likely to be?" Pick up the object and go search for the light.

**Pre-move check:** Before issuing any `go to` action toward the light source, verify that you are holding the target object. If not, stay in the current room and search for the object first. Do not move to the light until the object is in your inventory.

**Runtime check:** When near a device mentioned in the task (e.g., desklamp, floorlamp), scan admissible actions for a `use` option and execute it when appropriate.


- **Light-action check:** Before any action that involves the light source (e.g., `use desklamp`, `examine with floorlamp`, `go to desklamp`), verify that you are holding the target object. If not, take the object first.
- **Completion check:** After picking up the target object, if the task requires looking at it under a light, your next action must be to use the light source while holding the object. Do not stop or consider the task complete until you have executed that action.
## New Section

### Heat/Cool Tasks
When the task involves changing an object's temperature (cool, heat, chill, warm), follow this sequence:
1. Locate and pick up the target object first. Start with the most likely storage location: if the target is a perishable food, go to the fridge first; otherwise search typical storage spots (countertops, cabinets, drawers). Do not go to the appliance until you are holding the object.
 Once you have the object, do not place it anywhere; immediately go to the appliance. Runtime check: After picking up the target object, re-read the goal instruction. If it specifies a temperature change (cool, heat, chill, warm), do not place the object until you have executed the transformation.
2. Once holding the object, go to the appropriate appliance (fridge for cooling, microwave/toaster/stove for heating).

**Runtime check:** Upon arriving at the appliance, BEFORE any `open` or `move` action, scan the admissible actions for a direct heat/cool command involving your held object. If found, select it immediately; do not manually open the appliance or place the object inside. If the appliance is closed, check the admissible actions for a direct combined action (e.g., `heat <object> with microwave`). If present, use it immediately without opening; the action handles the appliance automatically. Only open the appliance manually if no direct combined action is available.
3. Use the direct combined action (e.g., `cool <object> with fridge`, `heat <object> with microwave`) while holding the object. Do not place the object inside the appliance first unless the combined action is not available. Runtime check: before executing any `move X to appliance` step, look for an entry in the admissible list that performs the heat/cool action with X directly.

**CRITICAL: If the admissible actions contain a direct heat/cool command (e.g., `heat potato 1 with microwave 1`), use it immediately. Do not manually place the object inside the appliance, close it, or open it. The direct command works even if the appliance is closed.**
4. After the transformation is complete, go to the target receptacle, open it if closed, and place the object using a `move` action. Before any `move` action that completes the task, verify that the heat/cool step has already been performed.


**Runtime check:** After arriving at the appliance, before any `open`, `move`, or `close` action, scan the admissible actions for a direct heat/cool command involving your held object (e.g., `heat tomato 2 with microwave 1`). If present, select it immediately; do not manually open the appliance or place the object inside.


**Efficient sequence:** Follow the pick → go to appliance → cool/heat → go to target surface → place sequence without detours. This avoids unnecessary intermediate stops and wasted actions.
## Common Pitfalls


- **CRITICAL: Revisiting empty locations:** Never revisit a container you have already opened and found empty. Keep a mental checklist of inspected locations and their contents. Before each `go to` action, explicitly ask: "Have I already visited this location and found it empty?" If yes, skip it and choose an unvisited location. Do not revisit a location unless you have a specific new reason (e.g., to place an object).
- **Closed containers:** If the observation says "The … is closed", your next action must be `open …` (if admissible). Do not move on or conclude the container is empty until it has been opened.  
  **Runtime check:** if the current observation contains “The <receptacle> is closed”, your next action must be to open it, not to go somewhere else or examine it while closed.
- **Unnecessary examination/navigation:** Do not inspect objects or move to extra locations unless the task goal explicitly demands it. Every action must advance the goal.


- **Ignoring visible furniture types:** Do not fixate on similar containers (drawers, cabinets) and ignore other furniture types (sidetables, beds, desks) that are visible and could hold the object. Systematically visit each distinct furniture type before repeating any container type. When searching for small objects like utensils, always include drawers in your search plan. After opening three cabinets without success, switch to drawers.
- **Searching closed containers before open surfaces:** Never open a closed container until you have inspected every open surface in the room. If you find yourself going to a cabinet or drawer, stop and verify that all countertops, tables, and shelves have been checked.

- **Revisiting empty containers:** After you have opened a container and confirmed it is empty (e.g., `On the drawer 1, you see nothing.`), do not return to it later in the same search loop. Mark it as visited and move on to the next unvisited location.

- **Returning to remembered locations too soon:** After placing a required object at the goal, if you still need more instances of that type, do not immediately go to a location you saw earlier. Instead, scan the admissible "go to" actions for any surface you have not yet checked (or any nearby surface that might contain the object) and visit those first. Only once nearby and unvisited candidates are exhausted should you travel to a previously seen location. Runtime check: While at the goal/receptacle and the task is incomplete, scan the current list of admissible actions. If there is a `go to <surface>` for a surface you haven’t inspected in this episode (or haven’t checked since picking up the last needed object), go there to look for the remaining target item before travelling to a remembered distant spot.

- **Fixating on a subset of surfaces when a required fixture is missing:** If you need a stationary fixture (e.g., desklamp, sink, stove) and it is not on the surfaces you have already checked, immediately visit every remaining open surface in the room (shelves, tables, etc.) before repeating any `take`, `move`, or `examine` actions. Runtime check: after exhaustively examining a surface and not finding the fixture, ask: "Are there any `go to` actions left in my admissible list that I have not yet tried?" If yes, take the first untried one before repeating any other action.
- **Redundant examination:** If you arrive at a location and the observation already describes its contents (e.g., 'On the cabinet 1, you see nothing'), do not use `examine`. The information is already provided; move on immediately.



- **Looping after task completion:** After performing a `move` or `place` action that you believe completes the task (e.g., placing a cooled pot on a counter), do not immediately pick up the object again or repeat the cooling/placing cycle. Verify that the task's goal has been met: check that the object is in the target location and any required transformation was applied. If satisfied, stop. If uncertain, use `inventory` or `look` to confirm, but do not repeat actions.
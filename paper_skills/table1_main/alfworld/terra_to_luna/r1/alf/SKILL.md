---
name: alf
description: "Embodied household-task skills distilled from execution experience."
---

## Core Approach


Before acting, decompose the task into an ordered checklist of sub-goals. Ask: "What are the two or three concrete steps I must complete, and in what order?" (e.g., acquire → clean → place). Execute them one at a time without detours. Runtime check: after deciding your next action, ask "Does this action directly complete the current subgoal or transition to the next required subgoal?" If not, reconsider.

- **Target-first navigation:** If the task specifies a target location (e.g., 'put X on Y'), make that location your very first destination before any search, **unless a transformation is required** (see Transformation Fixtures). This confirms whether the object is already there or reveals obstacles. If the object is present, take it, perform any required transformation, and then place it back. If not, proceed with search.


- **Setup actions for relational tasks:** When the task mentions an object in a specific relation to another (e.g., "look at X under Y"), identify both objects and any necessary setup actions (turning on a lamp, opening a container) as part of the sub-goal chain. For "look at X under Y" tasks: first navigate to the surface or container that hosts Y (e.g., the desk for a desklamp). This often locates both X and Y in one trip. Take X (if present), then use Y. If X is not there, search for it, but do not activate Y until you are holding X. Do not activate Y before taking X. Do not attempt to move or place X under Y—the `use` action completes the task. **Runtime checks:** Before moving, ask: "Is there a furniture item named in the goal or closely associated with the objects I need? If so, go directly to that item." Before interacting with the device, verify you are holding the target object or it is already at the device's location. If not, postpone the interaction until you have acquired the object. For example, "look at statue under desklamp": go to the desk first, take the statue, then use the desklamp.
## Precondition Chains


- When the goal mentions a “clean” object (e.g., “put a clean butterknife in drawer”), you must clean it at a sink before placing it. After picking up the object, go to a sink and issue `clean <object> with <sinkbasin>` immediately.

## New Section

## Transformation Fixtures

When the task involves a transformation verb (e.g., clean, cool, heat, chill, freeze, warm), immediately identify the static fixture that performs that action:
- **clean** → sinkbasin or bathtubbasin
- **cool / chill / freeze** → fridge
- **heat / warm** → microwave or stove

Visit that fixture as your very first destination, before any target location, to check if the object is already there and to prepare for the transformation step.

**Runtime check:** Before choosing the first navigation, ask: "Does the task require a transformation? Which fixture performs it?" Make that fixture your first destination.


- When you arrive at the transformation fixture while holding the target object, immediately use the direct transformation action (e.g., `clean <object> with <sinkbasin>`, `heat <object> with <microwave>`, `cool <object> with <fridge>`) if it appears in the admissible actions. Do not place the object on or inside the fixture unless no direct action is available.

**Runtime check after picking up the object:** Immediately after acquiring the target object, ask: "Does the goal require this object to be in a specific state (cool, hot, clean, etc.)?" If yes, go directly to the transformation fixture and apply the transformation before placing the object at the target. Do not place the object anywhere else first.

- **Verify state before transforming:** Before applying a transformation (clean, heat, cool, etc.) to an object, first examine the object to confirm it needs that transformation. If the object is already in the desired state (e.g., already clean, already hot), skip the transformation and proceed directly to placement. Runtime check: "Have I examined the object's current state and verified that the transformation is needed?"

- **Runtime check before any manual appliance interaction:** Before issuing `open`, `move`, or `close` on a microwave, fridge, or similar appliance, scan admissible actions for a direct transformation action (e.g., `heat`, `cool`). If present, use it immediately instead of any manual steps.
- For cooling, use `cool <object> with <fridge>` directly; do not open the fridge or place the object inside.
## Search Strategy


**Cardinal rule:** Once you have opened a container and seen its contents, never return to it unless you later need to place something there. Mark it as 'inspected' and move on.
- **Open surfaces first:** Never open a closed container (cabinet, drawer, etc.) until every open surface (countertop, table, sinkbasin, bathtubbasin, stoveburner, coffeemachine, etc.) in the current room has been visited and examined. If any open surface remains unvisited, go there before opening any closed storage.

- **Prioritize semantically plausible locations first, but always respect the open-surface-first rule:** Before starting a physical search, scan the initial observation list of accessible receptacles and identify those whose names or typical contents match the target object. Visit the most plausible open surfaces first (countertops, tables, etc.), even if a closed container seems more plausible. Only after all open surfaces have been visited should you move to closed containers, again prioritizing the most plausible among them. After exhausting the most plausible leads, fall back to a systematic sweep of the remaining receptacles.
Runtime check: If the target is not found after checking plausible surfaces, list all unvisited open surfaces (countertops, tables, shelves, etc.) and visit them in order before opening any cabinets or drawers. Do not skip any open surface, even if its name does not seem related. *Runtime check:* Before each navigation action, ask: "Have I visited all open surfaces? If not, which unvisited open surface is most plausible?" and go there next; if all open surfaces are done, then ask: "Which unvisited closed container is most plausible?" and go there. This applies even if you have a strong hunch the object is inside a cabinet—open surfaces must be cleared first.

- **Pre-search planning:** Before moving, read the initial observation and list every receptacle (closed containers and open surfaces) that could contain the target object. Plan a route that visits each exactly once. After visiting, mark it as done. This ensures no receptacle is missed and prevents repeated visits.

**Runtime check:** After each container inspection, consult your initial list of receptacles. If any receptacle on the list has not been visited, go to the first unvisited one in your planned order. Do not revisit any location until all have been visited.

- **Search open surfaces first, then closed containers:** first go to every open surface (countertops, tables, sinkbasin, bathtubbasin, stoveburner, coffeemachine, etc.) and examine what is on them. Only after all open surfaces have been visited should you start opening closed containers (cabinets, drawers). Runtime check: before opening or going to a cabinet/drawer, ask: 'Have I already gone to every open surface (countertop, table, desk, diningtable, etc.) listed in the admissible actions and examined what is on them?'
- **Then search containers in a fixed monotonic order:** exhaust one category (e.g., all cabinets in numerical order) before moving to the next (e.g., drawers). Use increasing numbers (cabinet 1→2→3…, then drawer 1→2→3…).
- **Track searched locations to avoid loops:** maintain a mental record of every location you have inspected and found empty. Never revisit a location unless you have a concrete reason to believe its contents have changed. Before choosing a `go to` action, ask: "Have I already visited this location, opened it if needed, and seen its contents?" If yes, skip it and move to the next unvisited location.

- **Before every `go to` command, verify the destination is not on your visited‑and‑empty list; also ask: "Is this the receptacle I just left? Are there any other unexplored receptacles (different names or numbers) that I could check first?" If either condition is true, skip it and move to an unexplored container.**
- **Runtime check for transformation fixtures:** Before revisiting a fridge, microwave, or sink that you have already inspected and found empty, ask: "Am I holding the object that needs cooling/heating/cleaning?" If not, do not go there; pick an unvisited candidate. Mark such fixtures as "searched, not useful until I have the object."
- If an observation explicitly states "nothing" on a receptacle (e.g., "On the sinkbasin 1, you see nothing"), treat it as definitively empty and never revisit it during the current search. Only return if you later place something there.

- **Never revisit a receptacle you have already inspected unless you later need to place an object there.** Before moving to a location, check your recent observations: if you have already visited that receptacle and found it empty (or opened it and found no target), skip it and move to the next unexplored one. Even if you are uncertain, trust your earlier inspection.


- **Inspect target container first when placing:** When the task involves placing an object at a specific location, navigate to that location first to check if the object is already there. If it is, take it, perform any required transformation (clean, heat, cool, etc.), and then place it back. If it is not there, proceed with the search strategy.
- **Open closed containers on arrival:** When you arrive at a closed container, open it to see its contents before deciding what to do next (contents are invisible until opened). If you are already near an adjacent container and an 'examine' command is available, you may examine it remotely to check if it's open or closed without moving.

- **Remote open:** If the admissible actions include an 'open <container>' for a container not at your current location, use it to open that container remotely, saving a move. Runtime check: After arriving at any new container, scan admissible actions for an 'open' command; if present, use it first to reveal what is inside. Only after seeing the contents should you choose your next destination.

- **Runtime check:** before moving to a different container type, verify that every instance of the current type (e.g., all drawers 1–6) has been opened and inspected. If any remain, go there next.
- **Runtime check:** after exhausting all containers of a type (e.g., all drawers), list the remaining unvisited furniture categories (e.g., shelves, tables) and navigate to the nearest unvisited container of the next type. Do not revisit any container you have already checked.
- **After open surfaces, skip fixtures during closed-container search:** Once all open surfaces have been inspected, when searching closed containers, do not visit fixtures like sinkbasin or bathtubbasin again unless you later need to clean something there. Only visit cabinets, drawers, shelves, desks, tables that could hold the object.
- **Before leaving a container, verify it is open:** after you have inspected its contents and are about to leave, check that the container is open. If it is closed, open it first to ensure you haven't missed anything.
- **Check sink area first for cleaning objects:** When the task involves a dishsponge, cloth, or any cleaning-related object, navigate directly to the sink (sinkbasin) as your first action, overriding the general search order. These objects are commonly found there.


- **Check fridge first for perishable food items:** When the task involves a food item commonly refrigerated (e.g., eggs, milk, vegetables), navigate directly to the fridge as your first action, overriding the general search order.
  - **Runtime check before first move:** If the task mentions a food item, ask: "Is the fridge accessible?" If yes, go to the fridge and open it if closed before exploring other locations.
  - **After checking the fridge:** if the object is not there, immediately revert to the standard search order: visit all remaining open surfaces (countertops, tables, desks, etc.) before opening any cabinets or drawers. Do not start opening cabinets until every open surface has been inspected.

  - **Runtime check after fridge miss:** Before opening any cabinet, list every open surface (countertop, table, desk, etc.) and the goal receptacle. If any remain unvisited, go there first.
- **Prioritize likely surfaces for common objects:** When searching for a specific object, consider its typical location (e.g., newspapers on coffee tables, bowls on desks, plates on tables, books on shelves). If you have a strong expectation, you may visit that surface first, even if it is an open surface, before starting the systematic closed-container search. If the object is not there, revert to the standard search order: visit all remaining open surfaces first, then closed containers.
- **Runtime check before first move:** Before issuing the first `go to` action, ask: "Which open surface (countertop, table, shelf) is most likely to contain this object?" and head there directly. If no open surfaces are available, ask: "Which closed container is most likely?" Never go to a closed container if any open surface remains unvisited.
- **Runtime check after arrival:** After arriving at the candidate surface, if the object is listed in the observation, take it immediately; otherwise move on to the next likely location or start the container search.

- **Map before you act (multi-object or transformation tasks):** When the task requires multiple objects or a transformation, before picking up any object, systematically explore all likely receptacles (open surfaces first, then closed containers) to locate all required objects and any necessary equipment. Do not take the first candidate you see; confirm it is the correct object and that no other required items are hidden. Runtime check: "Have I identified all required items and visited the most plausible receptacles for each before picking up the first?"

- **Take immediately if visible on open surfaces:** When you arrive at an open surface, the observation lists its contents. If the target object is among them, take it immediately; do not continue searching other locations.
- **Check stoveburners first for pots and pans:** When the task involves a pot, pan, or other cooking utensil, navigate directly to the stoveburners as your first action, overriding the general search order. These objects are commonly found there.
- **Remote take:** If the admissible actions include a `take <object> from <receptacle>` for the target object, even if you are not at that receptacle, execute it immediately. This can save navigation steps. Runtime check: after each action, scan the admissible list for a string containing both `take` and the target object's name; if found, select that action.
## Action Validity & Recovery


- At each step, select actions strictly from the provided admissible action list. Never attempt an action that is not explicitly listed as admissible.
Do not use `examine` on a container or surface if the current observation already lists its contents. Before choosing `examine`, check: “Do I already know what’s here from my last observation?” If yes, skip the examine and move on. Similarly, do not use `inventory` unless you have just picked up or placed an object; the observation already shows your held item or empty hands. Before `inventory`, ask: “Has my inventory changed since the last step?” If not, rely on the observation.

- **Avoid redundant examine on closed containers:** Do not use `examine` on a closed receptacle if you also have an `open` action for it. Opening it directly reveals its contents, while examining only tells you it's closed, wasting a turn. **Runtime check:** before using `examine`, ask: "Is this container closed and do I also have an `open` action for it?" If yes, use `open` instead.


- **Navigate before interacting:** Before issuing a `take`, `open`, `close`, `use`, or `examine` command on any object at a surface or container, ensure your immediately preceding action was a `go to` to that location. Runtime check: "Was my last action a go-to to this location?" If not, go there first.

- If the observation says 'you see nothing' on a surface or container, that is a content listing; do not examine it.


- **Multiple identical objects:** When you arrive at a location that lists several instances of the needed object (e.g., pillow 1, pillow 2, pillow 3), do not `examine` any of them. Directly `take` one and proceed. **Runtime check:** “Are multiple identical target objects visible? If yes, take one now without examining.”
## Task-Type Procedures


- **Object transport (single object)**: When the task requires only one object, after picking it up, go directly to the target container and place it there. Do not divert to check other locations while holding the object. For tasks requiring multiple objects, follow the Multi‑Object Tasks procedure.

- **Runtime check:** Before placing, verify the object is in your inventory (check 'You are carrying:') and that you are at the target surface (observation mentions it).
- **Runtime check after pickup:** Immediately after taking the target object (for single-object tasks), your next action must be `go to <target>` (unless you are already there). Do not examine, inventory, or visit other locations.


### Multi‑Object Tasks (combined actions)

When the task requires performing an action on a second object or fixture while holding the first (e.g., "put a bowl on the desk after turning on the desklamp"), identify all required objects before starting. After picking up the first object, carry it while searching for the second object or fixture, using the search strategy.

**Runtime check:** Before any action while holding the first object, ask: "Do I have the required tool? If not, am I about to examine or use the held object?" If the tool is missing, avoid examining or using the held object; instead, go to the next unvisited location to find the tool. Do not place the first object until you have completed the required action (e.g., turning on the lamp).

- **Runtime check:** Before executing `move ... to ...` or a repeated `examine` on the held object, ask: "Does this action bring me closer to finding the needed tool?" If the tool is still missing, avoid the action and go to an unexplored container. Before placing any object, verify that the required action has been completed.

### Object Placement (put X on Y)
> **Note:** This procedure applies only when the object does **not** require a transformation (clean, heat, cool, etc.) before placement. If a transformation is needed, follow the appropriate transformation procedure (e.g., 'Put a clean object in a receptacle') instead.

1. Navigate to the target surface Y.
2. After arrival, read the observation. If the goal object X is listed, take it and place it on Y (skip to step 5).
3. If X is absent, select the next unvisited plausible container (e.g., drawer, cabinet) from the admissible navigation list and go there.
4. Open the container immediately, take X, then navigate back to Y.
5. Before placing, confirm the observation mentions Y, then place X.

**Runtime checks:**
- After step 2, verify whether X is present; if not, move directly to an unvisited container without examining it.
- After step 4, ensure you are at Y (observation contains Y's name) before issuing the place command.


- **After arriving at the target with the object:** scan the admissible actions for a `move <object> to <receptacle>` command. If present, execute it immediately without any extra examining or looking around. Verify: “Am I at the target location and is a ‘move’ action available?” If yes, perform it without delay.

### Sequential Transport (multiple identical objects)

When the task requires moving multiple objects of the same type to a target location (e.g., "put two candles in drawer"), handle them one at a time: pick up one, go to the target, place it, then return to get the next. Do not attempt to carry more than one object at once.

**Runtime check:** After picking up an object, verify via observation that you are holding it, then proceed directly to the target location and place it before picking up another.

- **After placing an object, if you still need more copies, continue searching from the next unvisited receptacle, not the one you just left.**


- **Maintain a fixed forward order of candidate containers** (e.g., drawer 1 → drawer 2 → … → dresser). After picking up and depositing one copy, resume at the next unvisited container in that order; never revisit a container you have already opened or inspected earlier in the task. **Runtime check:** before issuing `go to <container>`, ask: “Have I already opened or examined this container during this task?” If yes, skip it and go to the next candidate in your ordered list.
- **Explicit action sequence after pickup:** After `take <object>`, the very next action must be `go to <target receptacle>` (unless you are already there), followed by `move <object> to <receptacle>`. Do not search for other objects or perform any other actions while holding a target object.
## New Section

### Placing objects into receptacles
When placing an object into any receptacle (cabinet, drawer, microwave, fridge, etc.), first ensure it is open. If the receptacle is closed, open it before attempting to place. Runtime check: "Is my target container closed? Then I must open it before placing the object."

### Put a clean object in a receptacle
For any task of the form "put a clean <object> in <receptacle>", follow this subgoal chain strictly in order:
1. **Obtain** the object (locate and take it).
2. **Clean** the object at a suitable fixture (sinkbasin, bathtubbasin) using the `clean` action.
3. **Place** the clean object in the target receptacle (go to receptacle, then `put` or `move`).

   - Before placing, verify the receptacle is open; if closed, open it first.

At each phase transition, verify: "Have I completed all three phases in order: obtain, clean, place?" Never skip directly from obtaining to placement without cleaning.

- **While holding the object:** After obtaining (and after cleaning), do not wander to any intermediate locations. Confirm from the observation that you are carrying the object, then go directly to the cleaning station, then directly to the target receptacle. Use `clean <object> with <fixture>` and `put <object> in/on <receptacle>` without detours.

   - After cleaning, before navigating to the target receptacle, confirm its type (e.g., drawer, cabinet) and that you will open it if closed upon arrival. Runtime check: "Is my next destination a receptacle that matches the task description? Will I open it if it is closed?"
## Common Pitfalls


- Before any `take` action, verify that the object's name matches the target phrase exactly (e.g., if looking for 'keychain', do not take 'remotecontrol' or 'creditcard').

- Avoid redundant inventory checks: only use `inventory` when your held items have changed (just picked up or placed).
- Revisiting containers you have already inspected and found empty. Once you have opened a container and confirmed the target object is not inside, mark it as 'done' and never return.
- **Moving objects into appliances unnecessarily**: When you are holding an object and arrive at a heating or cooling appliance (microwave, toaster, fridge, etc.), scan the admissible actions for a direct `heat <object> with <appliance>` or `cool <object> with <appliance>` action. If present, use it immediately instead of moving the object into the appliance. This avoids extra open/close/take steps.
- Before placing an object into a receptacle (e.g., fridge, cabinet, drawer), verify the receptacle is open. Prefer the `move <object> to <receptacle>` action for the final placement step. Runtime check: before executing the final `move` action, confirm the current observation shows the target receptacle is open.


- **Assuming all copies of an object are on the same surface:** When you need multiple copies (e.g., two newspapers), after picking up one from a surface, do not immediately return to that same surface. Instead, first visit other plausible surfaces (e.g., sidetable, coffeetable) that could hold the object, even if you previously saw multiple copies there. **Runtime check:** Before going back to a known location for a second copy, scan admissible destinations for a different surface that might hold the target; visit it first to avoid unnecessary backtracking.


- Re‑examining the same object or surface when a required tool is missing. Once you have picked up the first object and the tool is not present, immediately search other receptacles instead of examining the held object or its surface again. **Runtime check:** Before using `examine` on the held object or any surface you have already visited, ask: "Is the required tool still missing?" If yes, do not examine; go to an unvisited receptacle instead.

- **Trying to carry multiple objects at once:** You can only hold one item at a time. After picking up an object, deliver it to its target location and place it before picking up another. Do not attempt to pick up a second object while holding one.

- **Premature device interaction in composite tasks:** When the task involves using a device with an object (e.g., 'look at X under Y'), do not interact with the device until you have acquired X. Always obtain X first, then go to Y, then turn on/open Y. **Runtime check:** Before any `use <device>` action, check if the goal mentions an object that must be under/with that device. If yes, verify you are holding that object or it is present at the device's location; otherwise, postpone the action.

- **Leaving the target object behind after finding it:** Once you locate the object, take it immediately, even if you haven't yet found the target location or device. Only delay taking if the object is in a closed container and you need to open it first (open then take).


- **Picking up cleaning tools (dishsponge, cloth) unnecessarily:** Cleaning an object requires only the sinkbasin and the object. Use `clean <object> with sinkbasin` directly; never pick up a dishsponge or cloth. **Runtime check:** Before picking up any cleaning tool, verify the admissible actions at the sink include `clean <target> with sinkbasin`; if so, skip the tool.
- **Placing objects on cleaning fixtures unnecessarily:** When you arrive at a sinkbasin or bathtubbasin while holding an object that needs cleaning, do not place it on the fixture. Instead, look for a `clean <object> with <fixture>` action in the admissible list and use it directly. This avoids extra steps.

## Task Completion

**Stop after task completion:** Once you have placed the object at the target location and verified it is there (via observation or examine), the task is complete. Do not re-handle, pick up, or transform the object again. Runtime check: immediately after placing, examine the target receptacle; if the object is present, stop acting and do not issue further commands.
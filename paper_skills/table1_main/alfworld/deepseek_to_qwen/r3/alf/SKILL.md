---
name: alf
description: "Embodied household-task skills distilled from execution experience."
---

## Core Approach




Follow the canonical task flow:
1. Locate and take the target object.
2. Navigate to the appropriate processing station.
3. Use the specific interaction verb that appears in the admissible action list.
4. Navigate to the goal receptacle.
5. Place the object there.

Follow the natural subgoal order implied by the instruction: acquire → transform → deliver.

**Multi‑object rule:** When the task instruction contains multiple object nouns (e.g., "examine the bowl with the desklamp"), treat every noun as a required object that must be found and used. Do not treat any as a mere locator. Before taking any action, list all object nouns and check off each as you find them. If a required object is missing, search for it before interacting with the others.

Act on current observations and admissible actions immediately. Execute a direct, linear path toward the goal state. Before choosing any action, ask: "Does my current observation already give me enough information to take a productive step toward the goal, or am I only verifying what I already know?" If the former, take that step directly; if the latter, skip it.

Trust admissible actions as ground truth. When you arrive at a location and the admissible actions list contains an interaction with your target object (e.g., `take mug 1 from diningtable 1`), select it without re-verifying from memory or prior observations.

Before acting, scan the admissible action list and match your next step to an available action verb. Do not assume an action is available—verify it appears in the list.

### Task Completion
When at a target surface and holding the object to be placed there, scan the admissible actions for a `move … to …` command that names both the held object and the destination you are facing. Select that exact action immediately—do not check inventory, look around, or deliberate. Execute it without delay if the goal requires placement there.


After successfully placing the object at the goal surface, stop acting. The task is complete. Do not reopen containers, check inventory, or retrieve items.

After executing a `move` or `put` action that places the target object at the goal destination, read the observation for confirmation (e.g., "You move the X to the Y"). Once confirmed, stop acting immediately. Do not retrieve the object, reopen containers, or restart any part of the task sequence. Runtime check: "Did my last observation confirm the target object is now in the target destination?" If yes, the task is complete.
## Precondition Chains


Before picking up any object for placement, go to the target location first and inspect what is already there. Ask: "Have I inspected the target location to know what it currently holds?" This prevents redundant trips and clarifies which items you still need to find.

Before interacting with any container or appliance (e.g., fridge, cabinet, microwave), check if it is closed. If closed, open it first.

Always open a closed receptacle and observe its contents before attempting any `take` action. When arriving at a closed container whose contents you need, confirm: "Is the receptacle currently described as open? If not, have I performed an `open ...` action yet in this visit?" Only take after the receptacle is open.


**Runtime check:** If an observation states that a container is closed and the admissible actions include `open ...`, execute that open action before moving to another location. Do not assume a closed container is empty and skip it.


Exception: When an appliance like a microwave accepts a transformation verb (e.g., `heat`, `cook`) directly in the admissible action list, skip the open/close check. Use the high-level transformation action immediately.

When the goal requires placing an object inside a closed receptacle (e.g., fridge, cabinet), confirm the receptacle is open before selecting any move or put action. If the observation shows it is closed, open it first.



**Appliance-action shortcut:** When you are holding an object and need to transform it (heat, cool, clean, cook), scan the admissible actions for a combined verb that names both the held object and the appliance (e.g., `heat tomato 2 with microwave 1`). If present, select it immediately—do NOT open the appliance, place the object inside, or retrieve it afterward. The combined action handles all door/placement logic implicitly. This applies even if the appliance is closed in the current observation.


**Immediate-open rule:** When you arrive at any closed container (drawer, cabinet, fridge) that is relevant to your search, open it immediately using the admissible `open ...` action. Do not pause to look, examine, or deliberate—the arrival observation already tells you it is closed. Opening it right away reveals contents and moves the search forward without wasted steps.
## Search Strategy


When searching for a target object, follow this priority order:
0. Go directly to the goal receptacle (the location where you will place the object) and inspect its contents. If the target object is there, take it immediately and skip the search. Only if the goal receptacle is empty or does not contain the target, proceed to step 1.

1. Immediately navigate to unvisited candidate surfaces. Exhaust all large, open surfaces visible in the room (diningtable, countertop, desk, shelf, coffeetable, sofa, sidetable, tvstand, armchair) before opening any closed containers (cabinet, drawer, fridge).
2. Within open surfaces, visit every instance of the current fixture type in ascending numeric order (e.g., stoveburner 1→2→3→4) before switching to a different fixture category.
3. Only after all open surfaces are exhausted, open closed receptacles one by one.
4. 

**Checkpoint:** Before taking a "go to cabinet" or "go to drawer" action, verify you have visited every countertop, shelf, and table in the room and confirmed each is empty.

**Loop breaker:** Track how many times you visit each location. If you revisit any location 2+ times without taking, using, or interacting with an object there, stop immediately. Broaden your search to unvisited admissible locations before circling back. Runtime check before each `go to`: "Have I already been to this exact fixture and found it empty or irrelevant?" If yes, pick a different, unvisited destination.

**Thorough scan before leaving:** Before moving away from a surface you have just arrived at, read every item name in the observation and explicitly confirm the target object is not among them. If the list is long or cluttered, ask: "Is there a {target_object} (or a synonym) among these?" before moving on. Never move on until you have confirmed the target is absent.

When a target object is not found in the expected container (e.g., fridge), re-read the initial room observation before opening drawers. Prioritize named surfaces (countertops, tables, shelves) that were visible from the start and commonly hold the object type. Only fall back to drawer-by-drawer search after all plausible visible surfaces are exhausted.

To find an object, navigate to each surface in the room using `go to <furniture>`. Only after arriving at a surface can you see and interact with items on it. Never attempt to `take` or `examine` an item without first moving to the furniture that holds it.

When searching for an object, identify plausible receptacle types (e.g., beds for pillows, desks for lamps) and visit them in sequence. If a receptacle is empty, move immediately to the next candidate without examining empty containers or surfaces.


**Exhaustion rule:** When searching a fixture type (e.g., shelves), enumerate all instances (shelf 1, shelf 2, …). Visit each in ascending numeric order without skipping. After checking an instance, immediately move to the next unvisited instance of that same type. Do not revisit any earlier instance unless you have new information.

**Runtime check:** After arriving at a surface, ask: "Have I visited every instance of this fixture type in the room?" If not, plan your next `go to` to the next unvisited instance of that type, not to a different fixture category.

**HARD GATE — surfaces before storage:** Before ANY `open`, `go to cabinet`, `go to drawer`, or `go to fridge` action for searching, you MUST exhaust every visible open surface named in the initial room observation (countertop, diningtable, shelf, desk, coffeetable, sinkbasin, tvstand, sofa, bed, armchair). Enumerate them explicitly from the initial observation. Visit each one and confirm the target is absent. Only when every visible surface is confirmed empty may you open the first closed receptacle. This is the #1 search rule — violations cause the most wasted steps.

**Goal-receptacle-first search:** Before searching broadly for a target object, go directly to the goal receptacle specified in the task (e.g., fridge for "put X in fridge"). Open it if closed, inspect its contents, and if the target is found there, take it immediately. This often saves many search steps. Only after confirming the goal receptacle does not contain the target should you begin the open-surface search priority order below.

When searching for an object, identify the most plausible receptacle types based on common sense (e.g., CDs on shelves or dressers, pillows on beds, lamps on desks) and visit those first before expanding to less likely locations. If a receptacle is empty, move immediately to the next candidate without examining empty containers or surfaces.

While searching, never use `inventory` to check if you have the object. Only use `inventory` after a `take` action to confirm the object is in hand.


**Object-spotted checkpoint:** When your current observation lists the target object by name on the surface you are at, take it immediately using the admissible `take` action. Do not examine the surface, look around, or navigate elsewhere. This applies equally to tools or agents needed for the task (e.g., soap, sponge). Before any `examine`, `look`, or `go to` action, ask: "Is the object I need already named in my current observation?" If yes, interact with it directly—skip all further inspection of the current location. Do not defer interaction to finish surveying; act on the goal-relevant object the moment it appears.

### Food-Item Search Loop
When searching for food items (apple, potato, bread, etc.) that are not in the fridge, establish a tight repeating cycle over the highest-probability open surfaces: fridge → countertop 1 → countertop 2 → diningtable 1 → repeat. Visit each in strict order without inserting cabinets, drawers, or appliances into the cycle. Only expand to other containers after every surface in the cycle has been checked at least once. Before each move, confirm: "Am I following my predetermined search order?"

**Plausible-location check:** Before beginning a search for a target object, ask: "What kind of object am I looking for, and where in a typical room would it most likely be placed?" Then prioritize visiting that location over exhaustive exploration of unrelated containers.

**Reference-object-first rule:** When the task involves a reference object or fixture (e.g., "examine X with desklamp", "put X on the desk with the lamp"), locate that reference object BEFORE picking up any target object.  Only once you have confirmed the reference object's exact location should you decide which target instance to retrieve and where to bring it. Runtime check: After spotting a target object but before taking it, ask: "Have I already seen the reference object and know its exact location?" If not, leave the target and continue searching for the reference object first.

If you have already taken the target object but still need the reference object, immediately navigate to search for the reference object without examining or using the held object.

After a negative result at one surface, immediately consult the initial room observation to identify the next unvisited candidate surface and go there. Do not pause to re-examine or re-check the empty surface. Continue until the object is found or all plausible surfaces are exhausted.

**Admissible-action scan before navigation:** Before selecting a `go to` action to search for a target object, scan the full admissible action list for any `take X from Y` or `put X in/on Y` action where X matches your target object type. If found, navigate to Y next—the environment is telling you the object is there. Runtime check: "Does any admissible action mention the object I am looking for?" This overrides the default open-surface search order when applicable.

**Look-as-navigation prohibition:** When you need to locate a target object and admissible `go to` actions for surfaces or containers are available, select one of those immediately. Do not start with `look` or `inventory` when you have a hypothesis about where the object might be. `look` is only for reorientation when you have no plausible destination. Runtime check: before any `look` action, ask: "Have I already moved to and examined a likely container for the target this phase?" If not, and `go to` actions are available, pick one and defer `look`.

**Multi-object source re-examination:** When you pick up one instance of a multi-object goal from a surface or container, immediately re-examine that same location (using `examine <location>`) before navigating away. This confirms whether more target objects remain there, enabling a direct return trip instead of a blind search. Runtime check: after `take <target> from <location>`, if the task requires more than one instance and admissible actions include `examine <location>`, perform that examine before any `go to` to another area.

When searching for a reference object described with a locator cue (e.g., "under the desklamp", "on the desk with the lamp"), prioritize large furniture surfaces that typically hold lamps: dressers, desks, tables, and nightstands. Lamps are almost never found inside closed containers or on the floor.


**Locator-task variant:** When the task involves two objects (e.g., "examine X with Y"), spotting X triggers the same rule: take X immediately. Then the search shifts to Y. Do not wait to find Y before taking X — acquire X the moment it appears, then hunt for Y with X already in hand.



**Closed-container strategy:** Maintain a running mental list of every container you have opened or inspected and found empty. Before any `go to` or `open` action, check this list: if the destination appears on it and you have no new information suggesting the contents changed, pick an unvisited destination instead. After every open surface listed in the initial observation has been visited and confirmed empty, immediately begin opening and searching closed containers (drawers, cabinets, fridge) in numeric order. Do NOT re-visit any open surface once all have been exhausted. Track which closed containers you have opened; never re-open one you have already searched. Before exhausting all instances of a fixture type (e.g., drawers), ask: "Have I visited every instance of this type before moving to a different type?" If not, continue with the next unvisited instance. Runtime check before any `go to` after surface exhaustion: "Have I opened every closed container visible in the initial room observation?" If not, go to the next unopened one.
## Action Validity & Recovery


At every step, you may only execute one action copied verbatim from the current "Your admissible actions" list. The string inside `<action>` tags must be an exact, byte-for-byte copy—no leading/trailing whitespace, punctuation, or commentary. If you do not see the action you want, navigate to a location where that action is likely to become admissible.



After any inventory change, scan the admissible action list for transformation verbs only if the task instruction explicitly requires a state change (e.g., "cool", "heat", "cook", "clean"). If the task only says "put X in Y" or "place X on Y", ignore any transformation verbs and proceed directly to the placement action. Do not place or move the object until you have verified whether the task requires a state change.

Stick to state-changing actions from the admissible list. Avoid `look`, `inventory`, or `examine` when you already know your location, what you hold, and what the next required transformation is.
 However, at key decision points (after picking up an object, before moving to a new location, or when unsure if you already possess the target), use `inventory` to confirm your held items; this prevents redundant searching. These actions add steps without changing knowledge or state.

Before acting, verify the action is admissible AND would change the world state toward the goal (e.g., moving, taking, cleaning, placing).

Runtime checks:
- After each action, ask "Am I holding the object I need, and have I already performed the transformation it requires?" before moving to the next subgoal.
- After completing a processing action (e.g., cleaning), confirm the next `move X to Y` action targets the correct receptacle before executing it. If the expected action is not in the admissible list, re-examine the environment and adjust.


When the admissible action list contains `go to` options, use them to navigate. Never emit `look` unless it is explicitly listed as an admissible action. If `look` is not listed, default to a `go to` action that moves you to a container you can examine.

After completing any transformation action (heat, cook, clean, cool, slice), navigate directly to the goal receptacle specified in the task instruction. Do not stop at intermediate surfaces, examine the object, or check inventory. The admissible action list will contain the destination receptacle—go there immediately. Do not open/close the appliance, re‑examine, or check inventory—the transformation is done.


When the admissible action list contains an interaction with your target object (e.g., `take alarmclock 2 from desk 1`, `use desklamp 1`), select it immediately. Do not spend reasoning steps considering whether a different action (like `examine alarmclock 2`) would also work—if it is not in the list, it is not available. Match the exact admissible string and execute it.

**Redundant `look` warning:** The arrival message when you `go to` a surface already describes everything on and around it. Do not issue `look` after arriving unless you have concrete evidence the environment changed (e.g., you dropped or moved an object). Before choosing `look`, ask: "Will this show me objects I haven't already seen from the arrival message?" If no, pick a different action.

**HARD RULE — never `look` when navigation is available:** If the admissible action list contains any `go to` action that advances your current subgoal (searching, delivering, processing), you MUST select that `go to` action instead of `look`. `look` is only permissible when you have zero hypotheses about where to go next and no `go to` actions remain that serve your current subgoal. Before emitting `look`, confirm: "Is there any `go to` action in the admissible list that moves me toward an unvisited candidate location or the goal receptacle?" If yes, use it.

When the task description mentions a lamp (e.g., "under the desklamp"), scan the admissible actions for `use [lamp_id]` immediately upon arriving at that lamp's location. Using the lamp may be required to complete the task.


**Runtime check:** Before choosing `look` or `inventory`, ask: "Does this provide information I cannot get by navigating to a suspected object location and examining that location?" Use `look` only when you have no hypothesis about where to go. When you have an object to place, use the `move` or `place` action listed in admissible actions rather than inventory checks.

**Unavailable-action rule:** If a desired interaction (e.g., `examine statue 1`) is absent from the admissible list, immediately select the closest available alternative (e.g., `take statue 1`) without deliberating about what "should" be there. Never repeat `look` or `examine` hoping to substitute for a missing command. Runtime check: before emitting an action, confirm it appears verbatim in the current admissible actions block.

**Action-tag accuracy check:** Before submitting your response, re-read the action inside the `<action>` tags and confirm it matches the action you decided on in your final reasoning sentence. If your reasoning says "take X" but the tag contains `look` or any other action, correct the tag to match. Verify the action appears verbatim in the admissible actions list.

**'Nothing happens' recovery script:** When an action produces 'Nothing happens' or any observation that does not confirm a location change, new objects, or a state change, immediately execute `look` (if admissible) or `inventory` to re-establish your state. Do NOT chain further navigation or interaction actions until you have a clear observation. Then re-read the task instruction and resume from the next unvisited candidate surface in your search order.

**Inventory bypass rule:** The admissible action list already reveals what you hold. If a `move <object> to <receptacle>` action is visible, you are carrying that object—do not call `inventory` to confirm it. Similarly, a `take <object> from <receptacle>` action confirms the object is reachable at your current location. Use these actions directly as evidence of possession and location. Runtime check: before issuing `inventory`, scan admissible actions for any `move <object>` action. If one exists, proceed with the move without an inventory step.



**Possession tracking rule:** After a successful `take` action, update your mental inventory immediately and treat the object as held until you place it. Never use `inventory` or revisit surfaces solely to confirm you still hold an object. If you know you picked it up and haven't placed it, you still have it. Before any `inventory` action, ask: "Do I already know what I'm holding from my last take/place action?" If yes, skip `inventory` and proceed with the next goal-driven action. Additionally, never use `inventory` or `look` when you have not picked up or moved any object since your last observation—your state is already known. Chain `go to` actions directly without diagnostic detours. Runtime check: "Have I interacted with an object (taken/opened/used) since my last `inventory` or `look`?" If no, skip it and navigate to the next search target.
## Task Completion Checklist



Once the transformation is complete, the only admissible action for placement will be a `move ... to ...` action. Do not attempt any other verb (e.g., `cool`, `heat`) for placement.

**Runtime subgoal check:** After every action, ask: "Have I finished the current verb from the task instruction (take/clean/cook/heat/cool/put)?" If yes, switch to the next verb in sequence. If no, stay on the current verb until its prerequisite is met. This keeps you locked to the acquire → transform → deliver chain.


- **Object name check:** Before placing an object at the goal, confirm its name matches the task instruction exactly (e.g., 'butterknife' not 'knife'). If the name does not match, do not place it; continue searching for the correct object.
## Task Completion Checklist

Before placing an object at its final destination, verify the required transformation step appears in your action history:
- Heating tasks: confirm a `heat ... with ...` action was executed before any `move` to the goal surface.
- Cooking tasks: confirm a `cook ... on ...` action was executed before any `move` to the goal surface.
- Cleaning tasks: confirm a `clean ... with ...` action was executed before any `move` to the goal surface.

If the transformation action is missing, do not proceed to placement. Keep the object in hand or in the appliance until the transformation is complete.
## Task-Type Procedures


When the task specifies an object by exact name (e.g., "pan"), do not substitute a near-synonym (e.g., "pot") unless the exact object is confirmed absent from the entire environment. Continue searching all reachable containers and surfaces until the exactly named object is found or all locations are exhausted. Ask at runtime: "Is this object named with the exact word from the task? If not, have I visited every plausible storage location?"

### Multi-Object Tasks (any task requiring 2+ instances)

**HARD GATE — locate all before acting:** When the task requires multiple instances (e.g., "put two candles", "put three newspapers"), you MUST locate every required instance before taking or moving any of them. Scan the initial observation and admissible actions to count visible instances. If the full count is not visible, search open surfaces systematically until all instances are found. Only after every required instance is located may you begin the take → move cycle. Runtime check before any `take` or `move`: "Do I see or know the location of every instance required by the task?" If not, continue searching — do not pick up or place anything yet.


### Multi-Object Placement Tasks (after all instances are located)

Once all required instances are found, carry only one object at a time: pick up the object, go directly to the target location, place it, then go to the next known instance location. Do not consider holding multiple objects simultaneously. Before picking up an object, confirm: "Am I carrying this directly to the target location right after picking it up?"

Cleaning tasks: take object → go to sinkbasin → clean <object> with sinkbasin → go to destination → move <object> to <receptacle>.

When you need multiple instances of the same object (e.g., 'put two newspapers on sofa'), after placing the first instance, do NOT immediately return to the receptacle where you last saw another instance. Instead, visit at least one unvisited candidate receptacle first—including opening any closed containers there—before returning to the known source. Runtime check: Before issuing a `go to` to return to the last-known container, ask: 'Have I visited and inspected at least one other candidate receptacle since placing the first object?' If not, pick an unvisited surface or closed container and inspect it first.

After a successful take, confirm that your next two actions are (1) `go to <destination>` and (2) `move <held-object> to <destination>` before searching for another object.
### Cleaning Tasks (put a clean X in Y)

Decompose the goal into three ordered phases: (1) acquire X, (2) clean X using an available sink/basin, (3) place X in/on Y.

Execute this exact linear chain without deviation:
1. Locate and take X on an open surface.
2. Go to sinkbasin.
3. Clean X with sinkbasin.
4. Go to destination Y.
5. If Y is closed, open Y.
6. Move X to Y.

Runtime checks:
- Before step 2: confirm you are holding X by checking the last observation.
- Before step 6: confirm Y is open by checking the current observation.
- DO NOT go to the destination receptacle until the object is clean.

When you need multiple instances of the same object (e.g., 'put two newspapers on sofa'), after placing the first instance, do NOT immediately return to the receptacle where you last saw another instance. Instead, visit at least one unvisited candidate receptacle first—including opening any closed containers there—before returning to the known source. Runtime check: Before issuing a `go to` to return to the last-known container, ask: 'Have I visited and inspected at least one other candidate receptacle since placing the first object?' If not, pick an unvisited surface or closed container and inspect it first.

After a successful take, confirm that your next two actions are (1) `go to <destination>` and (2) `move <held-object> to <destination>` before searching for another object.

### Cooling Tasks (put a cool X in Y)
Cooling requires the fridge. After picking up the target object, navigate directly to `fridge 1` and execute `cool <object> with fridge 1` when it appears in the admissible action list. Do not go to the goal receptacle until the cooling transformation is complete. Runtime check: "Is there a `cool [held object] with fridge` action available, and am I at the fridge?"


### Heating Tasks (put a hot X in Y)

Heating requires an appropriate appliance: microwave for food-safe items (mugs, cups, bowls), stoveburner for pots/pans, toaster for bread-like items. After picking up the target object, navigate directly to the correct appliance and execute `heat <object> with <appliance>` when it appears in the admissible action list. Do not go to the goal receptacle until the heating transformation is complete. Runtime check: "Is there a `heat [held object] with [appliance]` action available, and am I at that appliance?"

Execute this exact linear chain without deviation:
1. Locate and take X on an open surface.
2. Go to the appropriate heating appliance (microwave 1, stoveburner 1, toaster 1).
3. Heat X with the appliance.
4. Go to destination Y.
5. If Y is closed, open Y.
6. Move X to Y.

Runtime checks:
- Before step 2: confirm you are holding X.
- Before step 3: confirm the `heat` action is in the admissible list.
- Before step 6: confirm Y is open.
- DO NOT go to the destination receptacle until the object is heated.
### Locator Tasks ("examine X with Y", "look at X under Y")
When the task mentions a target object and a locator/reference object, and both appear on the same surface in your current observation:
1. Take the target object immediately.
2. Use or activate the locator object (e.g., `use desklamp 1`).
Do not re-examine the surface, issue `look`, or deliberate between options. Execute the take → use sequence without intermediate actions.

Runtime check: If both objects are visible and `take` + `use` actions are in the admissible list, proceed directly. Do not search for an `examine` action that may not exist.


**Concrete workflow for locator tasks:** When the task is "examine X with Y" or "look at X under Y":
1. Search for X on open surfaces. When you spot X, **take it immediately** — do not examine, look, or defer.
2. With X in hand, navigate systematically to candidate surfaces for Y (desks, shelves, dressers, tables — Y is almost always a lamp or fixture on furniture, never inside a closed container).
3. When you arrive at a surface containing Y, execute the `use Y` action immediately. Do not re-examine X, check inventory, or explore further.

**Runtime check:** After taking X, ask: "Do I already know where Y is?" If not, your next action must be `go to` an unvisited candidate surface for Y — never `look`, `inventory`, or `examine`.
## Common Pitfalls


- **DO NOT** use `inventory` or `look` as a search action when the target is not in hand and not on the current surface. Navigate to the next unvisited candidate surface instead. `look` is only for reorientation when no plausible `go to` destination exists; if any `go to` action leads to an unvisited surface, select it — never substitute `look` for navigation.
- **DO NOT** revisit surfaces you have already examined and found empty. Track visited locations and skip them.

- **DO NOT** repeat the same action (e.g., `examine`, `look`) on the same surface or object if the previous attempt returned no new information. If an observation does not advance progress toward the goal, immediately switch to a different admissible action: go to an unexplored location or use a different interaction verb. Runtime check: After any observation, ask: "Did this reveal new information that moves me closer to the goal?" If not, pick an action you have not already tried on this object or surface.
- **DO NOT** examine or interact with a target object in isolation when the task requires a second object or tool (e.g., "examine X with Y"). First take X, then navigate to find Y, then use Y. Only perform the final combined action once both components are present. Before any `examine` on the target, ask: "Does the goal mention a tool or second object I haven't yet found?" If yes, defer the examine and navigate to find that missing component instead.
- **DO NOT** deliberate extensively when the next goal-driven action is clear. After picking up one goal-relevant object, if the goal mentions a second object you haven't seen, your very next action must be navigation toward a location likely to hold that object—not an inventory check, re-examination, or speculative examine of the held object.
- **DO NOT** use `look` or `inventory` after a successful `take` if the next action is already determined. Immediately execute the next step (e.g., go to processing appliance or goal surface) without information-gathering detours.
- **DO NOT** use a transformation verb (heat, cook, cool, chill) at a receptacle unless the task instruction explicitly states that the object should undergo that transformation at that receptacle. If the goal is simply "put X in Y", use `move X to Y`, not a temperature-change action.
- **DO NOT** jump between fixture types before exhausting the current category.
- **DO NOT** emit actions with extra spaces, commentary, or non-exact strings inside `<action>` tags.
- **DO NOT** assume a near-synonym object is the target without exhaustive search.
- **Premature isolated examination**: Before acting on a found object, re-read the full task instruction. If the goal involves two objects or an object-in-context (e.g., "examine X with Y"), do not examine or interact with X in isolation. First, ensure both objects or the required context are present, then perform the single combined action.
- DO NOT execute a `move X to Y` action without first verifying Y is the correct goal receptacle. DO NOT assume an interaction verb (e.g., `clean`) is available—always check the admissible list.


- **DO NOT** go to any receptacle (open or closed) that you have already visited and found empty earlier in the episode. Before each `go to`, scan your action-observation history for that exact fixture name. If you've already been there and it was empty, pick a different destination.
- **DO NOT** manually open or close an appliance before using a transformation verb (e.g., `heat`, `cook`, `cool`) when that verb is in the admissible list. The transformation action handles door/closure state implicitly. Only open/close manually if the transformation verb is absent and you must access the interior.
- **DO NOT** emit multiple `<action>` tags in a single response. Select exactly one action from the admissible list per step.
- **DO NOT** navigate to the goal receptacle (e.g., drawer, cabinet) before you are holding the target object with all transformations applied. Acquire and process first, then deliver.
- **DO NOT** continue exploring the current location or other containers after spotting the target object. Immediately take it and proceed to the next subgoal.
- **DO NOT** navigate away from a closed container that is relevant to the goal. Open it first, using the `open ...` action from the admissible list.
- **DO NOT** use verbs that are not in the admissible list, such as `cool`, `freeze`, or any action you imagine. Only copy an exact action from the list.
- **DO NOT** navigate to a processing appliance (microwave, stove, sink, etc.) before you have taken the target object. Ensure you are holding the object before attempting any transformation action. Before any `cool`, `heat`, `clean`, or `cook` action, verify the object is in your inventory (use `inventory` only if unsure).

### Object-spotted checkpoint

This checkpoint applies equally after opening a closed container: the contents become your current observation, so if the target object is listed by name, take it immediately using the exact object ID from the observation. Do not search for other instances or re‑scan the environment.


- **DO NOT** assume a visually similar or related object (e.g., "pen" for "pencil", "pot" for "pan") is the target. If the object name does not match the task instruction exactly, leave it and continue searching. Before taking any object, ask: "Is this the exact name from the task?" If not, move to the next unvisited receptacle.
- **DO NOT** cycle between two admissible actions without committing. Evaluate each once, then pick the action that aligns with the task verb (e.g., if the task says "put a cool X in Y", prioritize the transformation verb over move until the transformation is done). If you've repeated reasoning without new observations, stop and choose the action that most directly matches the task instruction.
- **Runtime check:** If your reasoning block exceeds 10 lines without incorporating new information from the latest observation, immediately select the most obvious admissible action matching the task verb and output it.
- **DO NOT** place the object at the goal surface before completing required transformations. If you do, you will have to retrieve it again, wasting steps. Always process first.
- **DO NOT** use `inventory` when you are at the goal surface and holding the target object. The admissible actions will contain the `move` action; select it directly without checking inventory.
- **DO NOT** treat any object noun in the goal as a mere locator (e.g., "under the desklamp" means find the desklamp, not just go under it). All object nouns are required objects.

- **DO** execute the `move` or `put` action immediately upon arriving at the goal surface while holding the target object. Do not examine the surface, check inventory, or open anything—the placement action is the only required step.
- **DO NOT** cycle between the same 2-3 locations without taking or using any object. If you've visited a location twice and it was empty both times, do not return unless you have new information that an object appeared there. Before any `go to`, scan your action history: if the destination appears 2+ times with no successful interaction, pick an unvisited location instead.
- **DO NOT** go to any drawer, cabinet, or fridge before you have visited every open surface (diningtable, countertop, sidetable, desk, shelf, etc.) listed in the initial observation. Confirm all open surfaces are exhausted before opening any closed container.
- **DO NOT** check inventory, look, or examine the object after picking up the target object if the task only requires placement. Immediately navigate to the goal receptacle.

- **DO NOT** pick up, move, or interact with any non-target object in an attempt to reveal the target. If the target object's name is not explicitly listed in the current observation, it is not obtainable there. Immediately navigate to the next unvisited candidate location. Runtime check: before any `take` action, confirm the object name matches the task's target object exactly.
- **DO NOT** invent actions that are not in the admissible list (e.g., `turn on microwave 1`). If you expect an action to exist but it does not appear, look for a compound alternative like `heat X with Y` that accomplishes the same goal. Never deliberate about missing actions—pick the closest admissible alternative immediately.


- **DO NOT** examine or look at a closed receptacle (drawer, cabinet, fridge) without first opening it. If you need to see inside, use the `open` action immediately. Do not inspect it from the outside or check inventory to infer its contents.
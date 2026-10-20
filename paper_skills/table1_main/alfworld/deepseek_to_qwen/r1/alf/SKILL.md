---
name: alf
description: "Embodied household-task skills distilled from execution experience."
---

## Core Approach


Maintain a mental inventory of held items. After picking up an object, treat possession as confirmed state — do not re-check inventory immediately or re-visit surfaces to verify you have it. Verify inventory at key decision points: before starting a new search phase, after completing a transformation (clean, heat, cool), and when deciding whether to search for or use an object. This prevents redundant actions without obsessive re-checking.

Track opened/emptied containers explicitly. Never re-visit a container previously found empty unless new information indicates its contents changed. Before searching an area, confirm you are targeting only unchecked containers.

Before acting, extract EVERY noun phrase naming a physical object from the goal (e.g., "bowl", "desklamp" in "examine the bowl with the desklamp"). Treat ALL as required objects to find or interact with. Never dismiss any as mere locator descriptors.

When you arrive at a closed container relevant to the goal, open it immediately as your next action. Check admissible actions for 'open <container>' and use it before navigating elsewhere. Do not leave a closed target container to explore other locations.

When the goal mentions a target object described by its spatial relationship to a reference object (e.g., "pillow under desklamp"):
Before picking up or moving ANY target object, first locate the reference object by systematically searching likely furniture surfaces. Only once you have confirmed the reference object's exact location should you decide which target instance to retrieve. Runtime check: after finding a target but before taking it, ask "Have I already seen the reference object and know its exact location?" If not, leave the target where it is and continue searching for the reference object.
1. Go to the target object's location and TAKE it into your inventory.
2. Only then go to the reference object's location.
3. Use the reference object or complete the task with the target object in hand.

Always go to the goal receptacle first (e.g., fridge for "put in fridge"), open it if needed, and inspect its contents before searching elsewhere. If the target object is there, take it immediately.

Prefer state-changing actions (take, go to, use, open, put) over passive inspection (look, examine). Before using "look" or "examine", ask: do I already know what to find and where? If yes, perform a state-changing action instead.

### Interpreting Object Adjectives
Treat adjectives on target objects ("cool", "warm", "chilled", "hot", "cold") as clues to the required appliance:
- "cool"/"cold"/"chilled" → plan to use the fridge after obtaining the object
- "warm"/"hot"/"heated" → plan to use the microwave or stove after obtaining the object

When you see such a modifier, immediately note the corresponding appliance and plan to visit it after you have the object. As a runtime check, ask: "Does the object adjective match the function of any appliance I can see?"

When the goal describes a target object by its spatial relationship to a reference object (e.g., "statue under desklamp") and both are visible on the same surface, execute immediately: (1) take the target object, then (2) use or activate the reference object. Do not re-examine the surface or deliberate between options — the take → use sequence is the correct procedure once both are visible.


Never use `look` or `inventory` as a first action or when you already have a scene description. The initial observation already lists the room's furniture and surfaces. Your first action must be `go to <furniture>` where the target is plausibly located. Runtime check before any `look` or `inventory`: "Is there an unvisited location from the initial scene list that commonly holds this kind of object?" If yes, navigate there instead.

When determining your first navigation target, ask: "Which furniture piece in my initial observation best matches the location implied by the task description?" Move directly to that furniture as your first action.
## New Section

## Observation & Tracking

When you view a surface or open a container, read every listed item name aloud in your reasoning. If the list is long or cluttered, ask: "Is there a {target_object} (or a synonym) among these?" before leaving. Never move on until you have explicitly confirmed the target is not present in the current observation.

Maintain an internal checklist (spoken in your reasoning) of every receptacle or surface you have examined, with its result (e.g., "fridge 1: empty; countertop 1: empty; countertop 2: bread, potatoes, no tomato"). Before choosing a new destination, verify from that list that it has not already been checked and found empty of the target.

When an observation (examine, look) on a surface or container reveals no new information, do NOT repeat the same action on that same object. Immediately move to a different unexplored location. Runtime check: after any observation, ask "Did this reveal new information that moves me closer to the goal?" If not, pick an action you have not already tried on this object or surface.

Before any `go to` action, verify aloud: "Have I already visited <destination> and found it empty of my target?" If yes, skip it and pick the next unvisited location from the admissible list. Never revisit a surface or container whose full item list you have already seen unless new information (e.g., placing an object there) changed its contents.

After picking up any object, do NOT check inventory — the observation already confirmed possession. Proceed immediately to the next required action (transformation or placement) without re-verifying.

When the current observation already lists the target object(s) and any required tool or reference object on the same surface, act immediately: take the target or use the tool. Do NOT re-examine, look around, or search other locations. Runtime check: before any `examine`, `look`, or `go to` action, ask "Does my current observation already show the object(s) I need?" If yes, pick a `take` or `use` action from the admissible list instead.

When you inspect a surface and the target object is not listed, immediately move to the next unvisited plausible surface without taking any non-target objects. Use the observation results to eliminate locations and drive your next navigation choice. In multi-object tasks, do not partially take objects from a surface — locate all required instances before moving any.
## Precondition Chains


Before any action that uses a container or appliance (put, take, cool, heat, clean, etc.), verify the target is open. If closed, open it first.
- Check: "Is the receptacle I need to use closed?"
- If yes: execute the open action before proceeding with the main operation.
- Example: To cool a pot in the fridge, first open the fridge, then cool the pot.

### Container Arrival Rule
Whenever you arrive at a container (fridge, cabinet, drawer, microwave, etc.) described as "closed", issue the corresponding `open` command before inspecting or taking anything from it. Check on arrival: "Is this container closed?" If yes, open it. If already open, no extra action is needed. This applies regardless of whether you intend to use the container or simply check its contents.

Runtime check: before any `move` or `take` action involving a container, verify the observation confirms the container is open. If closed, open it first.

Before any transformation action (cool, heat, clean, slice, move), verify you are holding the target object. If the object is visible on a surface but not in your inventory, take it first. Runtime check: before emitting `cool X`, `heat X`, `clean X`, or `move X to Y`, confirm X appears in your last inventory observation or was taken in the immediately preceding action.
## Search Strategy


Runtime check before beginning any search: "What kind of object is the target, and which furniture type(s) in this room typically hold such objects?" Start with those locations first.

### First-Action Rule for Search
When the target is not immediately visible, your VERY FIRST navigation must go to an open surface (countertop, diningtable, desk, shelf, sinkbasin, dresser) — NEVER a closed container (drawer, cabinet, fridge). Scan the initial observation for all furniture with visible items on them and visit those first. Only after exhausting every open surface may you open a closed container.

Runtime check before any `go to <closed container>`: "Have I visited every open surface listed in the initial room observation?" If no, go to the next unvisited open surface instead.

1. Identify all candidate containers (cabinets, drawers, countertops, etc.) that could hold the target based on object type.
2. Prioritize open surfaces before closed storage. Exhaust ALL visible surfaces (countertops, tables, desks, shelves) first. Only open closed containers (cabinets, drawers, fridges) after every open surface has been checked. At each step, ask: "Have I checked all reachable open surfaces for the target before opening this container?"
3. Order them and visit each exactly once. Exhaust one fixture type completely before switching to another—visit every instance in ascending numeric order (e.g., stoveburner 1, 2, 3, 4).
4. At each container: if closed → open it; if open → examine it.
5. If target is visible → take it. If not → go to next candidate immediately.
6. Runtime check: before navigating to a container, confirm you have not already observed its contents in a previous step. Never revisit known-empty receptacles.

When searching for multiple required items, follow a systematic order: group by furniture type or numeric index, and exhaust one group before moving to the next. When a required object is not visible, systematically visit EVERY unvisited surface/receptacle in the admissible locations list before re-checking any surface. Track which surfaces you've visited; do not linger at one location. After finding one required item, deposit it at a safe target location if accessible, then resume searching remaining unvisited containers in the same structured order. This prevents backtracking and missed containers.

### Goal-Driven Navigation
When a task goal mentions an object, immediately scan the current room observation to identify its parent furniture or container. Move directly to that location using the corresponding "go to" action from the admissible command list. Before moving, verify both that the target furniture appears in the observation text and that the specific "go to" command is present in the admissible actions.

### Container Inspection
Open every closed container (drawer, cabinet, fridge, etc.) immediately upon arriving at it. Inspect its contents before taking any other action. Do not stand idle in front of a closed container.

When the target is not visible in the initial observation, immediately begin a structured linear traversal: go to every reachable container or surface in numeric order (shelf 1, shelf 2, …), inspecting each exactly once. Advance to the next unvisited candidate after every inspection — do not repeat `look` or `examine` on the same location. Exhaust all unvisited admissible locations before any revisit; if you catch yourself about to `go to` a surface you've already checked, stop and pick an unvisited one. Runtime check: before any non-movement action, ask "Have I moved to a new location since my last inspection?" If not, move to the next unexplored location.

When a search of the primary target location (e.g., fridge) yields nothing, do not immediately leave the area. Scan your initial room observation for other large surfaces (diningtable, countertop, shelf) that were visible at the start. Visit those surfaces before opening any closed cabinets or drawers. Runtime check: after a failed find, ask: "Did I visit every surface name I saw in the first room observation that could reasonably hold this item?"

When an object is described by a spatial relationship to a reference item (e.g., "under desklamp"), prioritize large furniture surfaces (dressers, desks, tables, shelves) that typically host such reference items. Always navigate directly to these surfaces using `go to <furniture>` before attempting to take items from them — never try to retrieve objects from a distance without first moving to their parent furniture. Move to these surfaces first before checking smaller containers.

When searching for a food item (apple, tomato, bread, potato, lettuce, etc.), prioritize the fridge first, then countertops, then cabinets. For utensils, prioritize drawers. For non-food items, prioritize open surfaces first as described above.

When a container is open and its listed contents include an object matching your target, take it immediately using the first matching `take` action from the admissible list. Do not examine the container or check inventory first — the observation is authoritative. Runtime check: after opening a container, ask "Does any listed object match my target?" If yes, act on the first match.
### Target-Location-First Inspection
When the task requires placing objects at a specific location (e.g., "put X on Y"), your VERY FIRST action must be to navigate to the target location Y and inspect what is already there. Do not search drawers, cabinets, or other containers before this step. Only begin searching elsewhere if X is not already present on Y. This reveals which items are already present and which you still need to find, preventing redundant trips.

Runtime check: as soon as you read a "put X on/in Y" instruction, identify Y. Your first action must be `go to Y` and inspect its contents. Before picking up any object, ask: "Have I inspected the target location to know what it currently holds?"

If surface searches (countertops, shelves, tables) exhaust without finding the target, immediately pivot to closed containers (drawers, cabinets, fridges). Open and inspect each before re-checking any surface. Never re-visit a surface more than once unless new information indicates its contents changed.

When you find a target object in a multi-object task, pick up ALL visible instances at that location before moving on. If a "take" action for a visible object is missing from the admissible list, use `examine <receptacle>` or `look` to refresh the observation and surface the action. Do not depart with an incomplete set.

Before navigating to any closed container (cabinet, drawer, fridge), scan the current observation for all open surfaces (countertop, table, desk, shelf, sinkbasin, stoveburner) that you have not yet visited. Visit every unvisited open surface first. Only when no unvisited open surfaces remain may you move to a closed container. Runtime check: "Have I visited every open surface visible in the current room observation before choosing this closed container?"

When searching for a specific object type, identify the container category most likely to hold it based on common sense (e.g., CDs on shelves or dressers, books on shelves, clothes in drawers or laundry, food in fridge). Begin exploration with that category before expanding to less probable locations.

When searching for an object with a known typical receptacle (pillow → beds, lamp → desks, utensil → drawers), visit all instances of that receptacle type in sequence. If one is empty, advance to the next immediately without examining or lingering.


Example: for 'put toiletpaper on toiletpaperhanger', go to toiletpaperhanger 1 first to confirm it is empty. Then check countertops and other visible surfaces before opening drawers. Do not assume the hanger is empty — verify it.
### Open-Surfaces-First Checkpoint
Before navigating to a closed container (cabinet, drawer, fridge) as a new destination, run this mandatory check:
1. Scan the current observation text for every named furniture surface (countertop, diningtable, shelf, sinkbasin, desk, dresser, coffeetable, sidetable, tvstand, etc.). These surfaces may not yet show their items; you must visit them to see what is on them. When multiple open surfaces are visible, prioritize the most general-purpose flat surface (countertop, table, desk) over specialized fixtures (sinkbasin, toilet, bathtub) as the first location to check.
2. Confirm aloud: "Have I visited every one of these visible-surface locations?"
3. Only if the answer is YES may you proceed to a closed container.
This checkpoint overrides all other search heuristics. Visible surfaces always come first. Exception: for small, concealable objects (keys, pens, utensils), closed containers (cabinets, drawers) may be checked before open surfaces. However, for toiletpaper: ALWAYS check the toiletpaperhanger first, then countertops and other visible surfaces, before opening any drawer or cabinet. The hanger is a dedicated fixture and must be inspected before guessing about storage. For larger objects (pillows, books, plates, bowls, cups, candles, food items on counters), exhaust open surfaces first.

After visiting an open surface, if admissible actions include opening a closed container at that location (e.g., a drawer under the sidetable), open it before moving to the next surface. This ensures you do not miss objects hidden inside furniture at the current location. Runtime check: if the admissible actions contain any action starting with `open`, and you still need target objects, use that open action before issuing a navigation command that leaves the location.

During active search, NEVER use `look` as a standalone action. `look` returns a generic room description, not per-surface item lists. Instead, use `go to <surface>` to see exactly what is on each countertop, table, desk, or shelf. The observation after `go to` is always more informative than `look`. Runtime check before emitting `look`: "Do I have at least one unvisited surface I can `go to` instead?" If yes, navigate there — do not `look`.

When searching for a target object, identify ALL plausible receptacle types based on the object category (e.g., soapbar → shelves, countertops, sinkbasins; food → fridge, countertops, cabinets). Visit every instance of each plausible type before concluding the object is absent. Do not stop after checking only one category.

Example: if the initial observation lists coffeetable 1 and sidetable 1, visit them before opening any drawer or cabinet.

### Post-Fridge Checkpoint
When searching for food and the fridge is empty of the target, do NOT immediately open cabinets or drawers. Instead, visit every countertop, diningtable, and shelf listed in the current room observation — in numeric order — before touching any closed storage. Runtime check: "Did I visit every countertop and table visible in this room before opening a cabinet?"

### Exhaustive Type Sweep
When a candidate location of a given type (e.g., drawer 1) is empty, do NOT switch to a different receptacle type (e.g., cabinet). Instead, continue visiting ALL remaining instances of the SAME type in ascending numerical order (drawer 2, drawer 3, …) until every instance of that type has been inspected. Only after exhausting every instance of the current type may you move to the next receptacle category. Runtime check: "Have I visited every numbered instance of this receptacle type before switching?"

### Admissible Action Hints
When searching for a target object, scan the admissible action list for any `take <target-type> from <location>` or `put <target-type> in/on <location>` action. If such an action exists, navigate to that location immediately — it indicates the object is present there. This can shortcut exhaustive search. Runtime check: before visiting a location, ask "Does any admissible action mention the object I'm looking for?"

### Post-Negative-Search Re-Scan
After searching an expected container (fridge, cabinet, drawer) and NOT finding the target, pause and re-read the initial room observation from the episode start. Identify every open surface (countertop, diningtable, desk, shelf, sinkbasin) listed there that you have NOT yet visited. Visit those surfaces next — before opening any additional closed containers. Runtime check: "Did I just search <container> and find it empty? If yes, what open surfaces from the very first observation have I NOT yet visited?" Go to the first unvisited open surface from that list immediately.

### Multi-Object Rule: Locate All Before Moving
When the task goal specifies a count of objects (e.g., "put two candles", "put three books"), fully locate ALL instances before taking or moving any of them. Do not pick up the first match and carry it around while searching for the rest — this causes inventory confusion and wasted steps. Runtime check before any `take` or `move`: "Can I see or have I already located every object mentioned in the goal count?" If not, continue searching unvisited surfaces and containers without taking anything until all instances are found.


### Repeating-Cycle Search for Food and Common Objects
When the target is a food item or common household object not found on the first pass, lock into a fixed repeating cycle over the 3-4 highest-probability surfaces (fridge → countertops → diningtable → back to fridge). Do not expand to cabinets, drawers, or appliances until every surface in the cycle has been checked at least once. Before each move, verify: "Am I following my predetermined cycle order?" If the next action would leave the cycle, pick the next location in the cycle instead.

When a task requires a common object, identify the most probable receptacle type before moving. Runtime check: "Where would this object normally be stored in a kitchen?" Navigate directly to that fixture first. For food items, this is the fridge; for utensils, drawers; for books, shelves. Do not wander to multiple random receptacles unless the first fails.
## Action Validity & Recovery


After navigating to a container, check its state. If "closed," the next action MUST be `open <container>`. If "open" with only surface items listed, use `examine <container>` if available.

Do not pick up non-target objects to "reveal" a hidden target. The observation text is authoritative: if the target is not listed, it is not there.

Every action emitted inside `<action>` tags must be an exact, byte-for-byte copy of one string from the admissible-action list. No leading/trailing spaces, no extra punctuation, no reasoning text inside the tags. Before sending, verify: "Is this string identical to an admissible action with no modifications?"

- Before acting, confirm the action is admissible and directly advances the goal state. Avoid redundant `look` or `inventory` actions when you already know your location, what you are holding, and what the next required transformation is.
- Identify required transformations early (e.g., "clean" implies cleaning at a sink) and execute the sequence without backtracking or unnecessary verification.
- When you find an object mentioned in a "with X" goal phrase, immediately look for and execute an admissible action that directly uses that object (e.g., "use desklamp 1", "turn on X"). Do not move away without interacting with it.
- Always pick actions from the currently offered admissible actions list. Match the goal's verb: if the task says 'put X in Y', look for 'move X to Y' in the list. Never invent actions (e.g., 'cool', 'warm') that do not appear in the admissible list. After completing a subgoal (e.g., heating), scan admissible actions for the goal-matching verb before doing anything else.
- Prefer high-level interaction commands from the admissible action list (e.g., `heat X with Y`, `move X to Y`) over decomposing into lower-level open/close/put sequences.
- When an action verb directly matches part of the task goal, use that verb unless it fails.

Skip initial `look` and `inventory` when the task description and starting observation already list all visible room objects and inventory is known to be empty. Begin navigating to the first candidate container immediately.

- Before opening a closed appliance (microwave, toaster, oven, fridge), scan the admissible action list for a compound action that skips the open step (e.g., `heat X with microwave 1`, `cool X with fridge 1`). Use the compound action directly if available. Only open the appliance if the compound action is absent or you need to retrieve something already inside.

### Pre-Action Checklist
Before emitting any action, run this quick check:
1. Is the target object visible in the current observation text?
2. Does the admissible actions list contain a command that directly names that object (e.g., `take mug 1 from diningtable 1`)?
→ If YES to both: execute that action immediately. Do NOT use `look`, `inventory`, or any other passive action first.
→ If the target is NOT visible: move to the next unvisited container or surface.

Never speculate about actions not in the admissible list. If a desired action (e.g., `take`, `open`) is absent, navigate to a location where it is likely to become available. Before emitting any action, confirm the exact string appears verbatim in the current admissible actions block.

Emit exactly ONE `<action>` tag per response. Never output multiple action tags in a single reasoning block. The environment processes only the first action; subsequent tags are ignored or cause errors.

Never deliberate about whether an absent action would work. If an action string does not appear verbatim in the admissible list, drop it immediately and pick the nearest available alternative. Wasted reasoning cycles on missing actions caused repeated failures in practice.

When you arrive at the destination receptacle while holding the target object, immediately scan admissible actions for a `move <held object> to <current location>` command. The presence of this action confirms possession and completes the task — select it without any intermediate checks or delays.

When choosing between multiple admissible actions (e.g., `move X to Y` vs. `cool X with Y`), evaluate each option exactly once, then commit. If your reasoning repeats the same analysis without new observations, stop and select the action whose verb most directly matches the task goal (e.g., "put" → `move`). Runtime check: if reasoning exceeds 10 lines without incorporating new observation data, immediately output the best-matching admissible action.

After opening a container or inspecting a surface, match target objects using the exact object ID from the observation text (e.g., `lettuce 4`), not an assumed ID from the admissible action list. If the observation shows the target, take that specific instance immediately. Do not search for a different instance unless the observed one lacks a matching take action or needs a state change.


- If an action returns "Nothing happens" or an ambiguous observation that does not confirm movement or state change, stop and re‑establish your state immediately. Use `look` or `inventory` to re‑survey the area before taking any further navigation or interaction actions. Do not chain actions until the ambiguity is resolved.

3. If the task goal includes a transformation (heat, cool, clean, slice) and you are holding the target object, scan admissible actions for a compound action that combines the transformation with the appliance (e.g., `heat tomato 2 with microwave 1`). If present, execute it immediately — do not open the appliance or manually place the object inside.
## Task-Type Procedures


For ALL placement tasks (put X in/on Y), your first action must be `go to Y` to inspect the destination. This reveals whether X is already there and establishes the receptacle's state early. Proven effective across tasks.


### Clean-and-Place Tasks ("put a clean X in/on Y")

Decompose into three ordered phases before acting:
1. **Acquire**: locate and take X
2. **Transform**: go to a water source (sinkbasin, bathtub) and clean X with it
3. **Place**: go to Y and put X in/on Y

At task start, explicitly list these phases. Every action must serve exactly one phase.

After acquiring X, execute the transform and place phases without detours: go directly to the sink, clean X, then go directly to Y and place it. Never visit intermediate locations between these steps.
### Heating-then-Storing Tasks
After completing a heating step (e.g., microwave, stove), navigate directly to the receptacle named in the task goal. Do not detour or visit intermediate locations. Check admissible destinations for the target receptacle at runtime and go there immediately.

Runtime check: after heating, before taking the next `go to` action, verify that the destination matches the exact receptacle name in the task goal. Do not detour to intermediate locations.

After picking up an object that needs heating, go directly to the correct heating appliance and heat it — no intermediate stops for inspection or unrelated destinations. Identify the appliance by item type: microwave for mugs/cups/food-safe items, stoveburner for pots/pans, toaster for bread. Runtime check before any non-heating action after pickup: "Does this object need heating and am I heading straight to the right appliance?"

After a compound transformation action succeeds (e.g., `heat X with microwave 1` returns a confirmation observation), go directly to the target receptacle and place the object. Do NOT open the appliance again, do NOT re-examine the object, do NOT deliberate about whether the transformation completed. The success observation is authoritative. The next action must be `go to <goal receptacle>` followed immediately by `move <object> to <receptacle>`.
### Critical: Transform Before Placing
When the goal requires a property-modifying action (clean, heat, cool, slice), perform that transformation IMMEDIATELY after acquiring the object and BEFORE any placement. DO NOT place the object at the target receptacle and then retrieve it for transformation. Runtime check before any "move X to Y" action: "Does X need cleaning, cooking, or other modification per the goal? If so, have I performed that modification yet?" If not, go to the transformation station now — do not place X first.

After acquiring the target object, scan the admissible actions list for verbs matching the goal adjective: `cool`, `heat`, `clean`, `slice`. If a matching compound action exists (e.g., `cool bread 1 with fridge 1`) and the object is not yet in that state, execute the transformation BEFORE any `move` or `put` action. Do not treat the adjective as a descriptive label — it is a required state change.
### Multi-Object Placement Tasks
When the task requires moving multiple objects to a target location, carry only one object at a time: pick up one object, go directly to the target location, place it, then search for the next. Do not consider holding multiple objects simultaneously. Before picking up an object, verify: "Am I going to carry this directly to the target location right after picking it up?"

Runtime check after acquiring any object: "Am I currently holding the object I need, and have I already performed the transformation it requires?" If transformation is needed and not done, go to the transformation station before the destination.


After placing one instance and still needing another, do **not** immediately return to the last location where you saw another instance. First, list other plausible candidate receptacles (tables, shelves, drawers, etc.) that you have not yet visited. Visit at least one such new location and inspect it (including opening any closed containers) before returning to the known source. Runtime check: "Have I visited and inspected at least one other candidate receptacle since placing the first object?" If no, pick an unvisited candidate before going back to the known source.

Runtime check for non-transformation objects: after a successful `take` of a target object that needs to be placed at a destination (and no transformation is required), your next two actions must be (1) `go to <destination>` and (2) `move <held-object> to <destination>`. Only after placing the object may you search for the next one.
### Cooling Tasks

For cooling tasks, follow the same pattern as heating: after picking up the object, navigate directly to the fridge and use `cool X with fridge Y` when the compound action appears in the admissible list. Do not detour or inspect intermediate locations. The fridge is the default cooling appliance.
## Common Pitfalls


- Revisiting already-searched containers without new information
- Arriving at a closed container and leaving without opening it
- Taking irrelevant objects hoping to find the target underneath
- Running `inventory` or `look` instead of examining the current location or moving to the next candidate
- Do not assume a near-synonym (e.g., "pot" for "pan") is the target object. Match the exact task noun. If the named object is not yet found, continue searching all reachable containers and surfaces until you locate the exact name or exhaust the environment. Before interacting, ask: "Is this object named with the exact word from the task instruction?"
- Re-checking inventory for items already known to be held
- Re-visiting containers already opened and found empty
- Haphazard movement between unrelated furniture types during search
- Failing to deposit found items before resuming search, causing confusion about what remains to find

- Using `inventory` or `look` when you already have a scene description and unvisited candidate locations. These actions reveal nothing new. Navigate to the next unvisited surface from the initial observation instead.
- Revisiting a surface whose full item list you have already seen. Before selecting a `go to` destination, confirm aloud: "Have I already seen the items on <destination> earlier in this episode?" If yes, skip it.
- Leaving a primary search area after one negative result without first checking all visible surfaces from the initial room scan.
- Delaying the final placement. The moment your observation says "You pick up the <target>", the only admissible destination is the goal surface from the task instruction. Go there immediately and use `move <object> to <surface>`.
- Assuming a visually-similar object (e.g., "pen" for "pencil") is the target. Never substitute. Exhaustively search every navigable container and surface before settling. At runtime ask: "Have I visited every receptacle in admissible actions before accepting a substitute?" If no, keep searching.
- Do not waste cycles wishing for an unavailable action (e.g., `examine statue 1`). If a desired command is absent from the admissible list, immediately select the closest available alternative without further deliberation. Runtime check: before emitting an action, confirm it appears verbatim in the current admissible actions block — if not, pick the nearest match and proceed.
- Opening a closed appliance before checking whether a direct compound action (e.g., `heat X with microwave 1`) is admissible, creating unnecessary open/close cycles.
- Deliberating about an expected action (e.g., `turn on microwave 1`) that does not appear in the admissible list. If a needed action is missing, re-scan the list for the next admissible alternative that advances the task.
- Navigating to the goal receptacle (e.g., drawer, fridge) before acquiring and transforming the target object. Always complete acquisition and any required transformation (cleaning, heating, cooling) before moving to the final destination.
- Arriving at the goal receptacle while holding the target object and failing to place it immediately. When you arrive at a location and the goal says to put something there, scan admissible actions for `move [held object] to [current location]` and select it without delay. Do not `examine`, `look`, or check `inventory` first — the presence of a `move` action for your held object is authoritative confirmation that you hold it and are at the right place. Runtime check: "Did I just navigate to the target location while holding the correct object?" If yes, find and execute the `move` action immediately.

- Skipping a required transformation (cool, heat, clean) after acquiring the target object. When the task goal includes a state modifier like "cool," "warm," "clean," or "chilled," immediately check admissible actions for a matching transformation command (e.g., `cool bread 1 with fridge 1`) and execute it before moving to the final destination. Never go directly to the placement location with an untransformed object.
- Using `look` or `inventory` after arriving at a location when you already have a clear hypothesis about where the target is. Navigate directly to the suspected container or surface. Use `look` only when you have exhausted all candidate locations and have no hypothesis about where to go next.
- Leaving a surface immediately after taking one instance of a multi-object goal without re-examining it. After `take <target> from <location>`, if the task requires more than one of that object, use `examine <location>` before navigating away to confirm whether additional instances remain there.
- Calling `inventory` to confirm possession when the admissible action list already contains a `move <object> to <receptacle>` action. The presence of a `move` action for an object is authoritative evidence that you hold it. Skip the inventory check and proceed directly with the move.
- Interacting with (examining, using, or moving) a target object in isolation when the goal requires a second object or context (e.g., "examine X with Y"). If the goal mentions two objects, acquire both before performing any action on either. Do not examine or use X alone — gather all required items first, then execute the combined action.
- Failing to interact with a reference object (e.g., a lamp) when the goal describes a spatial relationship to it. When a lamp or similar activatable object is visible near the target, scan admissible actions for `use <object>` and activate it immediately after taking the target.

- Using `look` when you have a specific candidate receptacle to check. `look` returns sparse observations from a distance; instead, navigate directly to the next unvisited receptacle (`go to <receptacle>`) and read the arrival observation. Runtime check before `look`: "Am I already standing at a concrete receptacle that matches the goal context?" If not, `go to` the next candidate instead.
- Failing to take a target object the moment you see it at a receptacle. When your arrival observation lists the target object and a `take ... from ...` action is admissible, execute that take immediately before any other action. Do not examine, look, or navigate away first.
- Continuing to search or explore after the goal conditions are satisfied. Once you hold the target object AND are at a receptacle containing the required complementary object (e.g., desklamp for "examine with desklamp"), execute the goal-fulfilling action (`use`, `put`) immediately. Do not visit additional locations.
- Checking `inventory` when the initial observation or last action does not confirm you are holding the target. Before using `inventory`, ask: "Did a previous action or observation explicitly state I am holding the target object?" If no, skip inventory and search the environment immediately.
- Emitting `look` or `inventory` when the admissible actions list contains a movement or interaction command that directly advances the goal. After reasoning about your next step, scan the admissible list for the verb that matches your plan (e.g., `go to`, `take`, `open`, `move`) and use that exact string. If `look` is not the only action that resolves genuine ambiguity, do not use it.

- Examining a target object alone when the goal requires a tool or second object (e.g., "examine X with Y"). Never `examine` X before you have located and activated/used Y. First take X (if needed), then navigate to find Y, then interact with Y. Only attempt the final combination action once all components are present. Runtime check: before `examine` on the target, ask "Does the goal mention a tool or second object I haven't yet found or activated?" If yes, defer the examine and navigate to find that missing component instead.
- Emitting a different action than the one you just reasoned about. After deciding on an action, verify that the action string inside `<action>` matches the action you concluded with. If your reasoning says 'take soapbar 2', your `<action>` must be `take soapbar 2 from countertop 1`, not `look`. Runtime check: before submitting, read the action you wrote and confirm it is the same action you just decided to take.
- Falling into repetitive navigation loops (visiting the same 2-4 locations repeatedly without taking, using, or transforming any object). If you have visited the same set of locations ≥3 times with no new interactions, immediately break the cycle: scan admissible actions for an unvisited location and go there. Runtime check: count how many times you have visited your current target location; if ≥2 and no object was taken or used there, pick an unvisited admissible location instead.
- Navigating to a closed drawer or cabinet as the first search action when open surfaces (diningtable, countertop, desk, shelf) with visible items exist in the initial observation. Always exhaust open surfaces before touching any closed container.
- Revisiting the same location more than twice without new information. If you catch yourself about to `go to` a surface or container you already checked and found empty, STOP. Use `look` once to reorient, then pick the next unvisited location from the admissible list. Do not cycle between a small set of locations — expand to unvisited ones immediately.
- After picking up a target object and receiving confirmation ("You pick up the..."), re-examining, re-verifying inventory, or deliberating about other instances. The next action must be navigation to the destination receptacle — no intermediate steps.
- Accepting a near-match object name (e.g., "knife" for "butterknife") and placing it without completing required transformations. Before placing ANY object, verify aloud: (1) "Does this object's name EXACTLY match the goal's target noun?" and (2) "Have I performed EVERY required transformation verb (clean, heat, cool, slice) on this object?" If either answer is NO, do not place it — continue searching or transform it first.


- After successfully placing the target object at the goal location and receiving confirmation (e.g., "You move the X to the Y"), re‑acquiring the object and repeating the transformation/placement cycle. Once the final placement is confirmed, the task is complete; do not pick up the object again.
- Retrieving an object from a heating appliance (microwave, stove, toaster) without having executed a `heat`/`cook` action on it first. If you `take X from microwave 1` but your action history contains no `heat X with microwave 1`, you have NOT heated the object — do not proceed to placement. Return the object to the appliance and execute the missing transformation. Runtime check before any `take X from <appliance>`: "Did I explicitly execute a heat/cook action on X in this appliance?" If no, do not take it out — heat it first.

- Confusing placement with transformation when the destination is an appliance. If the goal says "put X in/on Y" and Y is a microwave, fridge, or other appliance, use `move X to Y` — not `heat X with Y` or `cool X with Y`. Only use temperature-change actions when the goal explicitly says "cool", "heat", "cook", or "chill" with that appliance. Runtime check: before selecting an action at an appliance, ask "Does the goal say 'put' or 'place' here, or does it explicitly name a temperature change?" If it says put/place, use `move`.
- Manually opening an appliance and placing an object inside (or taking it back out) when a direct compound action (e.g., `heat X with microwave 1`) is available. Use the compound action directly without any intermediate open/close or place/retrieve steps.
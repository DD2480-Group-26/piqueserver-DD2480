# Report for Assignment 3

This report documents our project details, the onboarding experience, complexity analysis, refactoring plans, and coverage evaluation. The structure follows the provided template, ensuring clarity and consistency across all sections.

---

## Project

**Name:** *piqueserver*  
**URL:** *https://github.com/piqueserver/piqueserver*  

**Description:**  
The repository we evaluated for this project seems to handle game logic for a game called Ace Of Spades.

---

## Onboarding Experience

The onboarding experience was not completely painless. The documentation is split between a visible `README.md` on GitHub and a separate documentation website, and the instructions on these two sources conflict.

- **Initial Steps:**  
  - We initially followed the instructions on the documentation website to run the code and tests.
  - This approach failed because the dependency requirements did not download as expected.

- **Resolution:**  
  - We then used the recommendations at the bottom of the GitHub page.
  - Once the proper dependencies were downloaded (automatically into a virtual Python environment), the code ran without errors.

- **Dependency Documentation:**  
  - The required dependencies exist in a configuration file but are not explicitly stated in the documentation. 

---

## Complexity

### Complexity Measurement

We analyzed several complex functions using both manual counts and the Lizard tool. Below is a summary of our findings:

1. **Functions Selected for Analysis:**
   - `do_move` (lines 48-101 in `./piqueserver/core_commands/movement.py`)
   - `join_squad` (lines 161-223 in `./piqueserver/scripts/squad.py`)
   - `on_spawn` (lines 251-286 in `./piqueserver/scripts/squad.py`)
   - `on_chat` (lines 693-720 in `./piqueserver/scripts/markers.py`)

2. **Measurement Results:**
For each of our chosen function we peer-review the Cyclomatic Complexity count two and two.
   - **Manual Count:**
     - *`do_move`:* Both Adam and Love counted 18.
     - *`join_squad`:* Both Love and Adam counted 17.
     - *`on_spawn`:* Both Filip and Robin counted 20.
     - *`on_chat`:* Both Robin and Filip counted 15.
   - **Lizard (Cyclomatic) Complexity:**
     - *`do_move`:* **19**
     - *`join_squad`:* **20**
     - *`on_spawn`:* **20**
     - *`on_chat`:* **16**

3. **Observations:**

  **Question 3.1**
  ***What are your results for four complex functions?***
   * Did all methods (tools vs. manual count) get the same result?
   * Are the results clear?

The tools vs. manual count did not get the same result for the functions. We have understood that it can differ a lot with how you implement the method of counting the cyclomatic complexity and even the formula varies between theories.We used the formula that was shown during the lecture of structural complexity which is defined thusly: 
```
      M = pi - s + 2
      pi = number of decisions (if, while, and, or)
      s = (throws, returns)
```
According to the documentation of the lizard tool (https://pypi.org/project/lizard/) the way the cyclometric complexity is computed is mostly compatible with McCabe’s theory which gives us a different answer from us. 

  **Question 3.2**
  ***Are the functions just complex, or also long?***
In our case, the complex functions are also long. Although there is a correlation between complexity and length, the function’s purpose ultimately guides its design.

4. **Function Purposes:**
- **`do_move`:** (lines 48-101 in `./piqueserver/core_commands/movement.py`)
Moves a character within a 3D game environment.

- **`join_squad`:** (lines 161-223 in `./piqueserver/scripts/squad.py`)
The purpose of the functions is to manage the process of a player joining or leaving a squad. It has a number of different checks. It verifies that a player can join a squad, It determines whether the player is actually trying to change their current squad or follow preference. It also checks that there is space in the squad and if a player joins a squad, removes the player from an existing squad, if applicable. It also notifies the other player of the squad change. Since the function does a lot of things is 

- **`on_spawn`:** (lines 251-286 in `./piqueserver/scripts/squad.py`)
The on_spawn function is a method that runs when a player spawns in the game. It seems one of its primary functions is handling squad-based spawning, ensuring that the player is near their squad members, and updating squad-related information like setting safe spawn locations.

- **`on_chat`:** (lines 693-720 in `./piqueserver/scripts/markers.py`)
The on_chat method runs whenever a player sends a chat message. The method handles chat messages and determines whether they should trigger the placement of markers in the game based on if the message contains the command for that action. The method also ensures that markers are placement respects cooldowns, and it calculates appropriate positions for the markers placed.


5. **Exceptions and Documentation:**  
   - Did it take into account exceptions? 
   The manual coverage measurement tool we implemented relies on the user to add code to all the branches of the function so in a way it takes operations like ternary operators into account but it still relies on the user to add the needed code inside of the condition.

   - Is the documentation clear regarding possible outcomes: 
   The functions we worked with does not have any documentation apart from small comments in the code which do not provide a significant amount of information. The comments in the code are also NOT up to PEP-8 standard and are often just comment what a single line of code does.


---

## Refactoring

**Plan for Refactoring:**
We plan to refactor the complex functions to reduce their cyclomatic complexity. The aim is to improve maintainability while being mindful of any potential drawbacks, such as performance trade-offs.

- **Estimated Impact:**  
  Reducing complexity (and thus lowering the CC value) is expected to make the code easier to maintain. However, this might introduce other issues 

**Current Status:**  
- **`do_move`:** (lines 48-101 in `./piqueserver/core_commands/movement.py`)
The function can be improved in a number of ways. In the function is there a significant amount of code for parsing the position. This can be moved to function like this 
```python
def _parse_target_position(connection, args, arg_count, initial_index):
    if arg_count in (1, 2):
        # The target is specified as a <sector>.
        x, y = coordinates(args[initial_index])
        x += 32
        y += 32
        z = connection.protocol.map.get_height(x, y) - 2
        position = args[initial_index].upper()
    elif arg_count in (3, 4):
        # The target is specified as <x> <y> <z>.
        x = min(max(0, int(args[initial_index])), 511)
        y = min(max(0, int(args[initial_index + 1])), 511)
        z = min(max(0, int(args[initial_index + 2])),
                connection.protocol.map.get_height(x, y) - 2)
        position = '%d %d %d' % (x, y, z)
    else:
        raise ValueError('Wrong number of parameters!')
    return x, y, z, position
```
We could also Encapsulate the logic that figures out whether the command is moving the caller or another player, including permission checks in the following way:
``` python
def _determine_target_player(connection, args, arg_count):
    if arg_count in (1, 3):
        # Moving self: ensure the connection represents a valid player.
        if connection not in connection.protocol.players.values():
            raise ValueError("Both player and target player are required")
        return connection.name
    elif argount in (2, 4):
        # Moving another player: check permissions.
        if not (connection.admin or connection.rights.move_others):
            raise PermissionDenied("moving other players requires the move_others right")
        return args[0]
```
- **`join_squad`:** (lines 161-223 in `./piqueserver/scripts/squad.py`)
The function can be also improved in a number of ways. The code should be broken into more parts. The code for checking if a player is in a valid team should be added to a different function that we can define as:

```python
def _is_valid_team(self):
    # Returns True if the player is on a valid team.
    return self.team is not None and self.team is not self.protocol.spectator_team
```
The code for checking squad changes can also be separated out into a function which looks as follows:
```python
def _has_squad_changed(self, squad):
    if squad is None or self.squad is None:
        return self.squad is not squad
    else:
        # When both are provided, use a case-insensitive comparison.
        return self.squad.lower() != squad.lower()
```
Doing these changes would make the code easier to maintain and understand.

- **`on_spawn`:** (lines 251-286 in `./piqueserver/scripts/squad.py`)
There are some parts of the `on_spawn` function which could be refactored and other which could be seperate to reduce complexity.
You could, for example, create a helper function for getting all the members of a squad `_get_all_members(self)`, or a helper function which returns all the living members of a squad `_get_live_members(self, members)`. You could also create a seperate function for squad messages, `_build_squad_message(self, members)`, because alot of the branches lies in generating these chat messages.This would reduce code duplication and complexity for the function and therefore reduce the functions cyclomatic complexity in it whole.
Example code using helper functions:
```python
def on_spawn(self, pos):
    if self.squad:
        all_members = self._get_all_members()
        live_members = self._get_live_members(all_members)
        message = self._build_squad_message(all_members)
        if all_members:
            self.send_chat('You are in squad %s with %s.' % (self.squad, message))
        else:
            self.send_chat('You are in squad %s, all alone.' % self.squad)        
        if (self.squad_pref is not None and self.squad_pref.hp and
            self.squad_pref.team is self.team and not self.squad_pref.invisible and not self.squad_pref.god):
            self.set_location_safe(self.get_follow_location(self.squad_pref))
        else:
            if live_members:
                self.set_location_safe(self.get_follow_location(random.choice(live_members)))
    return connection.on_spawn(self, pos)
```


- **`on_chat`:** (lines 693-720 in `./piqueserver/scripts/markers.py`)
In `on_chat` you could reduce complexity by writing helper functions for determining whether marker is on cooldown, determining the marker location, and finding the matching marker class. This will reduce the complexity becuase a lot of logic is moved outside of the function by having helper functions (there will be less if-statements etc. in `on_chat`). You can also reduce complexity a lot by having early returns for when the helper functions return none or false. The early returns would increase the amount of returns which reduces complexity according to the formula `M = pi - s + 1`, where `s` is the amount of returns.

---

## Coverage

### Tools

**Using `coverage.py`:**  
We first employed the `coverage.py` tool to measure branch coverage across our codebase.

- **Documentation:**  
  The tool is well-documented, though initially it was challenging to interpret the output. The results from the tool were hard to interpret before we realized that the tool, even with the branch flag set, would output branch and line coverage together. We therefore had to parse the output to only get the branch coverage since we are only interested in that and we did this using a simple python script.

- **How to run the tool**:
 We use Coverage.py, version 7.6.12 with C extension and Python 3.10.12
  In the root of the repository run: 
  - coverage run --branch -m pytest
  Followed by: 
  - coverage json -o coverage.json
  This generates a JSON file in the root of the directory. Then run the script disp.py which genereates a html page. To display it, run the following command in the root of the piqueserver directory. 
  - python -m http.server
  The report should then be visible at: http://localhost:8000/branch_coverage.html

  

- **Integration:**  
  Instead of integrating it into our build environment, we ran it from the command line and generated an HTML report for local review, as indicated above.


**Coverage Results (from `coverage.py`):**
- **`do_move`:**
  - Branches: **18**
  - Coverage before addings tests: **0%** since there were not tests for the function
  - Coverage after adding tests: **77.8%**
- **`join_squad`:**
  - Branches: **24**
  - Coverage before addings tests: **0%** since there were not tests for the function
  - Coverage after adding tests: **79.2%**
- **`on_spawn`:**
  - Branches: **16**
  - Coverage before addings tests: **0%** since there were not tests for the function
  - Coverage after adding tests: **100%**
- **`on_chat`:**
  - Branches: **12**
  - Coverage before addings tests: **0%** since there were not tests for the function
  - Coverage after adding tests: **50%**


### Our Own Coverage Tool

We also developed a custom coverage tool that works as follows:

- **Implementation:**  
  A Python dictionary is used where branch IDs are keys set to `False` initially. When a branch is executed by the tests, its corresponding value is set to `True`. After test execution, the tool returns the dictionary, indicating which branches were covered.

- **Results from Our Tool:**
  - **(`do_move`):** (lines 48-101 in `./piqueserver/core_commands/movement.py`)
    - Branches: **13**
    -  Coverage after adding tests: 10 out of 13 (~77%)

  - **(`join_squad`):** (lines 161-223 in `./piqueserver/scripts/squad.py`)
    - Branches: **16**
    -  Coverage after adding tests: 13 out of 16 (~81%)

  - **(`on_spawn`):** (lines 251-286 in `./piqueserver/scripts/squad.py`)
    - Branches: **12**
    - Coverage after adding tests: 6 out of 12 (~50%)

  - **(`on_chat`):** (lines 693-720 in `./piqueserver/scripts/markers.py`)
    - Branches: **9**
    - Coverage after adding tests: 5 out of 9 (~55%)


### Evaluation

1. **Detail Level:**  
   Since we have inserted the “branch counters” in each branch of the functions the measurement is reasonably detailed.
2. **Limitations:**  
   The limitation of our tool is that it is not dynamic. It must be done manually for each of the functions that you want to measure the coverage.
3. **Consistency:**  
   The results for the second function differ between our tool and `coverage.py`. It is not consistent because Coverage.py counts every possible branch in the bytecode, including both outcomes of each condition and each sub-condition in compound expressions. In our manual instrumentation do we only consider branching due to if-statements and while-loops. Coverage does also handle  Another thing is that our tool does not capture implicit branches. An expression like:
    `if self.team is None or self.team is self.protocol.spectator_team:`
is a compound condition. Coverage.py counts the two operands separately (and the implicit false outcome), so it can add more branches than you have instrumentation markers.


---

## Coverage Improvement

- **Requirements for Improved Coverage:**  
  Detailed comments have been added to describe the requirements for enhancing branch coverage.
- **Reports:**
  - [Old Coverage Report](link)
  - [New Coverage Report](link)
- **Test Cases Added:**  
  - Command used to view the patch: `git diff ...`  

---

## Self-assessment: Way of Working

- **Current State:**  
  Our current workflow is assessed according to the Essence standard.
- **Team Assessment:**  
  The self-assessment was conducted unanimously, though there remain minor uncertainties regarding some items.
- **Areas for Improvement:**
  We are currently in the “In-place” state, which is an improvement compared to where we were in the last project and is unanimous. We are comfortable in our communication and conscious of what we can expect from one another. The potential for improvement could be to start the project earlier to not be in a rush when approaching the deadline.                 
  We also identified potential improvements in documentation clarity, test coverage consistency, and overall team coordination.

---

## Overall Experience

- **Main Take-aways:**  
  
- **Learning Outcomes:**  
 
- **Additional Comments:**  


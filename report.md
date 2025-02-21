# Report for Assignment 3

This report documents our project details, the onboarding experience, complexity analysis, refactoring plans, and coverage evaluation. The structure follows the provided template, ensuring clarity and consistency across all sections.

---

## Project

**Name:** *piqueserver*  
**URL:** *(https://github.com/piqueserver/piqueserver)*  

**Description:**  
The code is a simple server for running the game Ace of Spades
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

 **Functions Selected for Analysis:**
   - **Function 1:** `do_move` (lines 48-101 in `./core_commands/movement.py`)
   - **Function 2:** `apply_script.join_squad` (lines 161-223 in `./piqueserver/piqueserver/scripts/squad.py`)
   - **Function 3:** `apply_script.on_spawn` (lines 251-286 in `./piqueserver/scripts/squad.py`)
   - **Function 4:**  `apply_script.on_chat` (lines 693-720 in `./scripts/markers.py`)

1. **Measurement Results:**
   - **Manual Count:**
     - *First Function:* Adam counted 17, Count by Love:  18
     - *Second Function:* Love’s count was 17, Count by Adam: 17
     - *Third Function:* Count by Filip: 20	Count by Robin: 20
     - *Fourth function*  Count by Robin: 15   Count by Filip: 15
   - **Lizard (Cyclomatic) Complexity:**
     - First function: **19**
     - Second function: **20**
     - Third function: **20**
     - Fourth function: **16**

2. **Observations:**
   - The tools vs. manual count did not get the same result for the functions. We have understood that it can differ a lot with how you implement the method of counting the cyclomatic complexity and even the formula varies between theories. We used the formula that was shown during the lecture of structural complexity which is defined thusly: 
	- M = pi - s + 2
	- pi = number of decisions (if, while, and, or)
	- s = (throws, returns)
According to the documentation of the lizard tool (source) the way the cyclometric complexity is computed is mostly compatible with McCabe’s theory which gives us a different answer from us. 


   - In our case, the complex functions are also long. Although there is a correlation between complexity and length, the function’s purpose ultimately guides its design.

3. **Function Purposes:**
- **`do_move`:**  
The do_move function teleports a player to a specified location, either a named sector or explicit coordinates, while enforcing permission checks. It determines the target position based on the provided arguments and ensures the player has the necessary rights to move others if applicable.
- **`join_squad`:**  
The purpose of the functions is to manage the process of a player joining or leaving a squad. It has a number of different checks. It verifies that a player can join a squad, It determines whether the player is actually trying to change their current squad or follow preference. It also checks that there is space in the squad and if a player joins a squad, removes the player from an existing squad, if applicable. It also notifies the other player of the squad change. Since the function does a lot of things is 
- **`on_spawn`:**  
The on_spawn function is a method that runs when a player spawns in the game. It seems one of its primary functions is handling squad-based spawning, ensuring that the player is near their squad members, and updating squad-related information like setting safe spawn locations.
- **`on_chat`:**
The on_chat method runs whenever a player sends a chat message. The method handles chat messages and determines whether they should trigger the placement of markers in the game based on if the message contains the command for that action. The method also ensures that markers are placement respects cooldowns, and it calculates appropriate positions for the markers placed.


4. **Exceptions and Documentation:**  
   - Did it take into account exceptions? 
   Exceptions are taken into account using our own tool as “s” in the formula stated above.
   The lizard tool for python does only look for  'if', 'for', 'while', 'and', 'or',
    'elif', 'except', 'finally' so it probably handles exceptions, but we could not find any mention of it in the documentation. 
 
5.
   - Is the documentation clear regarding possible outcomes: The second function does not have any documentation apart from small comments in the code which do not provide a significant amount of information.


---

## Refactoring

**Plan for Refactoring:**  
We plan to refactor the complex functions to reduce their cyclomatic complexity. The aim is to improve maintainability while being mindful of any potential drawbacks, such as performance trade-offs.

- **Estimated Impact:**  
  Reducing complexity (and thus lowering the CC value) is expected to make the code easier to maintain. However, this might introduce other issues 

- **Current Status:**  

---

## Coverage

### Tools

**Using `coverage.py`:**  
We first employed the `coverage.py` tool to measure branch coverage across our codebase.

- **Documentation:**  
  The tool is well-documented, though initially it was challenging to interpret the output. The results from the tool were hard to interpret before we realized that the tool, even with the branch flag set, would output branch and line coverage together. We therefore had to parse the output to only get the branch coverage since we are only interested in that.

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
- **First Function:**
  - Branches: **18**
  - Coverage before addings tests: **0%** since there were not tests for the function
  - Coverage after adding tests: **77.8%**
- **Second Function:**
  - Branches: **24**
  - Coverage before addings tests: **0%** since there were not tests for the function
  - Coverage after adding tests: **79.2%**
- **Third Function:**
  - Branches: **12**
  - Coverage before addings tests: **0%** since there were not tests for the function
  - Coverage after adding tests: **94%**

- **Fourth function**
  - Branches:
  - Coverage before addings tests: 
  - Coverage after adding tests: 


### Our Own Coverage Tool

We also developed a custom coverage tool that works as follows:

- **Implementation:**  
  A Python dictionary is used where branch IDs are keys set to `False` initially. When a branch is executed by the tests, its corresponding value is set to `True`. After test execution, the tool returns the dictionary, indicating which branches were covered. Our tool supports......

- **Results from Our Tool:**
  - **First Function (`do_move`):**
    - Branches: **13**
    -  Coverage after adding tests:: 10 out of 13 (~77%)
  - **Second Function:**
    - Branches: **16**
    -  Coverage after adding tests:: 13 out of 16 (~81%)

  - **Third function:**
    - Branches: 
    - Coverage after adding tests:: 
  - **Third Function:**
    - Branches:
    - Coverage after adding tests:


### Evaluation

1. **Detail Level:**  
   The measurement is quite detailed, as we have inserted branch counters in each decision point.
2. **Limitations:**  
   Our tool is not dynamic and requires manual instrumentation for each function under test.
3. **Consistency:**  
   The results for the second function differ between our tool and `coverage.py`. They differ because 

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

We are currently in the “In-place” state, which is an improvement compared to where we were in the last project and is unanimous. We are comfortable in our communication and conscious of what we can expect from one another. The potential for improvement could be to start the project earlier to not be in a rush when approaching the deadline.

---

## Overall Experience

- **Main Take-aways:**  
  
- **Learning Outcomes:**  
 
- **Additional Comments:**  


Using Python 3.9

### Table of Contents
- [Purpose](#purpose)
- [How to Run](#how-to-run)
- [Outside of Scope](#outside-of-scope)
- [Input](#input)
  - [1. users](#1-users)
  - [2. f_uniqueID](#2-f_uniqueid)
  - [3. history](#3-history)
  - [4. historyLimit](#4-historylimit)
  - [5. history_ParticipationRequired](#5-history_participationrequired)
  - [6. f_compatibility](#6-f_compatibility)
  - [7. f_restriction](#7-f_restriction)
  - [8. minUsers](#8-minusers)
  - [9. maxUsers](#9-maxusers)
- [Output](#output)
- [Feature Ideas](#feature-ideas)

# Purpose 
This library takes a list of users and assigns them to other users. Consider prior exchanges and custom restrictions. 
- Examples include things like, an Art Trade or Gift Exchange

Handles various object types for User by allowing for lambda funtions to:
- identify a user uniquely (Ex: if the User object has a unique_ID or primary_key variable)
- check if a user is restricted from being pairedwi th another user (Ex: user's can't be paired with users on the same team.)

Methods to customize user combinations:
1. No closed pairings. (currently not editable)
    - Example of a closed pair: A gets assigned B, but B is also assigned to A. 
2. uses Exchange history for limiting assignments
    - Ensure that each user gets assigned to someone they haven't been assigned to for a specified amount of exchanges. 
    - can build user history based on if they participated in prior Exchanges
3. Custom *compatibility* for weighted assignments
    - Providing a function, you can prioritize pariring with users who are "more compatible than others"
4. Custom *restrictions* 
    - By providing a custom function, you can set restrictions. 
        - Example: no user can be assigned someone on the same team.

# How to Run
1. download the gift_exchange.py into your project
2. in your project, import the library with ```from gift_exchange import *```
3. run ```GiftExchange()``` using the desired parameters - see the *Input* selection below for info there
4. Evaluate the results and decide if you want to add to a user history.

Specific examples are in the test cases.


# Outside of Scope 
- Managing assignment *history*, such as:
    - adding the results to the history, accepting or rejecting the results is determined outside this module
	- managing the unique ID's of the user in the history. (if the ID's change in anyway)
 
# Input 
## 1. users
- Status: Required
- What is it: 
    - List of unique objects of users
- These parameters use this one in their calculations: 
    - `f_uniqueID`
    - `f_compatibility`
    - `f_restriction`
  
## 2. f_uniqueID
- Status: Optional
    - Default value:
        ``` 
		lambda x: x 
		```
- What is it: 
    - Lambda function: 
        - input: user object
        - output: that object's unique ID
            - Note: Do NOT return a hash of the object. Since the user's individual variables can change which changes the hash value.
- When is it used: 
    1. Creating Assignment History
    2. Comparing users to historical assignments
- When is it NOT used:
    1. You're not looking to save memory. Like if User objects are small
    1. User objects themselves ARE the unique ID's
       - Example, if they are strings/integers.

## 3. history
- Status: Optional
    - Default value: Null
- What is it: 
  - List of dictionaries, representing previous assignment results.
    	- First item (index=0) being the most recent assignment.
    	- Both the key and value in the Dictionary represent the output of FUNC_UNIQUE_ID
    	- Key_user is who was assigned the value_user
  - Assignments are stored by "trade" instead of each users' individual history so we can look at individual trade results. We lose that information when only storing a user's assignment history.
- Expected to work with these paramerts: 
    - `f_uniqueID`

## 4. historyLimit
- Status: Optional
    - Default value: Null
- What is it: 
    - Positive int. A user cannot be assigned with someone ther've been assigned with the last times. Outside of this X value, assignments are "weighted", meaning that a user is with the person they've been assigned with the LEAST. When there is a tie... idk

## 5. history_ParticipationRequired
- Status: Optional
    - Default value: False
- What is it: 
    - Boolean (True/False). 
    - `history_ParticipationRequired == TRUE`, means exchange focused
        - Regardless of a user's participation in prior Exchanges the historyLimit relates to the number of exchanges that occurred
    - `history_ParticipationRequired == FALSE`, means user focused
    	- Tracks the history of the user ONLY for the times they participated. Meaning user's who don't participate often are still not assigned people they've given to in the last X exchanges where x == historyLimit

## 6. f_compatibility
- Status: Optional
    - Default value: Null
- What is it: 
    - Lambda function: calculates the likelyhood a user should be assigned to another.
        - input: two users
            - first = giver
            - second = receiver
        - output: a number, **Smaller the number, the less likely it is to occur.** 
    - Example: users closer in age are more likely to be paired
		```
		f_compatibility = lambda x, y : abs(x.age - y.age)
		compatibility = f_compatibility(user_a, user_b)
		```
- Randomized Shuffle of Weighted Items:
    - Formula: 
        ```
        random[between 0 and 1] ^ (1/weight)
        ```
        - Implementation speed: O(n log(n))
    - Reference Paper: http://utopia.duth.gr/~pefraimi/research/data/2007EncOfAlg.pdf
    - Description: while it sorts well enough, it's not quite ideal for what I need and I'll probably change it out sometime.
        

## 7. f_restriction
- Status: Optional
    - Default value: Null
- What is it: 
    - Lambda function: 
        - compares two users and returns if the Assignment is restricted, meaning they're not allowed to pair
        - input: two user objects
            - first = giver
            - second = receiver
        - output: boolean, True/False
    - Example: 
		```
		f_restriction = lambda x, y : x.team == y.team
		is_restricted = f_restriction(user_a, user_b)
		```

## 8. minUsers
- Status: Optional
    - Default value: 3
- What is it: an int which checks for the minimum number of users needed for the trade.

## 9. maxUsers
- Status: Optional
    - Default value: 50
- What is it: an int which checks for the maximum number of users needed for the trade.

# Output 
1. dictionary of assignments = 
    - key = the GIVER in the Exchange, represents the output from f_uniqueID for that user
    - value = the RECEIVER in the Exchange, represents the output from f_uniqueID for that user

# Feature Ideas
These are features I'd like to implement in future versions of the code
1. Have fall back Restriction calculations, in case no assignment configurations can be found with the current restrictions.
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
Assign Users to eachother in Giver-to-Receiver relationships for scenarios like: Gift Exchanges or Art Trades. 
Robust enough to handle different object types for User. 
Allows for modifications to posbible combinations, for things like: 
- uses Exchange history for limiting assignment options
- compatability of how likely a user is to be assigned to another
- flat out restrictions to other users (ex: no users can be assigned someone on the same team)

# How to Run
1. Install python
    - there should be no extra modules you download 
    - though a disabled test case uses the matplotlib library
2. download the gift_exchange.py into your project
3. in your project, import the library with ```from gift_exchange import *```
4. run ```GiftExchange()``` using the desired parameters - see the *Input* selection below for info there
5. Evaluate the results and decide if you want to add to a user history.

Specific examples are in the test cases.


# Outside of Scope 
- Managing assignment *history*, such as:
    - adding the results to the history: accepting or rejecting the results is determined outside this module
	- managing the unique ID's of the user in the history. (Ex: if the user ID's change in anyway)
 
# Input 
**Note**: Only *users* is a required field
## 1. users
- **What is it**: Users participating in this trade. 
- **Type**: List of unique objects of users. 
    - Robust enough to be various types of data: numbers, strings, custom classes (see parameters for this. start with "f_")
- **Where is it used**: 
    - `f_uniqueID` parameter
    - `f_compatibility` parameter
    - `f_restriction` parameter
  
## 2. f_uniqueID
- **What is it**: used to find a way to uniquely identify a user object. 
- **Type**: Lambda function
    - input: user object
    - output: that object's unique ID
        - Note: Do NOT return a hash of the object. Since differences in the user's internal values can change the hash value.
- **Default value**:
    ``` 
    lambda x: x 
    ```
- **Where is it used**: 
    1. `history` parameter
    2. Creating the final output
- **Depends on**:
  - `users` parameter

## 3. history
- **What is it**: Represents previous assignment results.
    - Assignments are grouped *by-exchange* instead of *by-user*. Meaning we can look at individual trade's results. We lose that information if we store results by-user.
- **Type**: List of dictionaries
    - First item (index=0) being the most recent assignment.
  	- Dictionary
    	- key = userID of a "giver"
    	- value = userID of a "receiver"
    	- **Note**: userID is the output of the `f_uniqueID` parameter
- **Default value**: empty list [ ]
- **Depends on**:
    - `f_uniqueID` parameter


## 4. historyLimit
- **What is it**: This limits who a user can be assigned for an exchange depending on prior exhange assignments, using the `history` parameter. (see the `history_ParticipationRequired` paramter for details on who is considered)
- **Type**: Positive integer
- **Default value**: 0


## 5. history_ParticipationRequired
- **What is it**: Determines if the program should care if a `user` participated in previous trades or not when considering the `historyLimit` paramter. 
    - Clarification: 
        - False = only check how many exchanges have occurred. 
        - True = check the prior assignments of that user (ignoring exchanges they didn't participate in)
- **Type**: Boolean (True/False) 
- **Default value**: False

## 6. f_compatibility
- **What is it**: Calculates the likelyhood a user should be assigned to another, then uses some randomization for "wiggle"
- **Type**: Lambda function
    - input: two users
        - first = giver
        - second = receiver
    - output: a number, **Smaller the number, the less likely it is to occur.** 
    - Example: users closer in age are more likely to be paired
        ```
        f_compatibility = lambda x, y : abs(x.age - y.age)
        compatibility = f_compatibility(user_a, user_b)
        ```
- **Default value**: Null
- **Depends on**:
    - `users` parameter
- **Randomized Shuffle of Weighted Items**:
    - Formula: 
        ```
        random[between 0 and 1] ^ (1/weight)
        ```
        - Implementation speed: O(n log(n))
    - Reference Paper: http://utopia.duth.gr/~pefraimi/research/data/2007EncOfAlg.pdf
    - Thoughts: while it sorts well enough, it's not quite ideal for what I need and I'll probably change it out sometime.
        

## 7. f_restriction
- **What is it**: Compares two users and returns if the Assignment is restricted, meaning they're not allowed to pair
- **Type**: Lambda function
    - input: two user objects
        - first = giver
        - second = receiver
    - output: boolean, True/False
    - Example: 
		```
		f_restriction = lambda x, y : x.team == y.team
		is_restricted = f_restriction(user_a, user_b)
		```
- **Default value**: Null
- **Depends on**:
    - `users` parameter

## 8. minUsers
- **What is it**: Checks for the minimum number of users needed for the trade.
- **Type**: Integer
- **Default value**: 3

## 9. maxUsers
- **What is it**: Checks for the maximum number of users needed for the trade.
- **Type**: Integer
- **Default value**: 50

# Output 
1. dictionary of assignments = 
    - key = the userID of the "giver" in the Exchange
    - value = the userID of the "receiver" in the Exchange
    - **Note**: userID is the output from passing a user object to the `f_uniqueID` parameter

# Feature Ideas
These are features I'd like to implement in future versions of the code
1. Have fall backs calculations for things like: HistoryLimit and Restrictions. This is in case no assignment configurations can be found with the current restrictions and we need a little "give".
2. Consider alternatives to the `weightedShuffle` method used in the `f_compatibility` paramter
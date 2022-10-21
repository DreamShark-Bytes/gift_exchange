Using Python 3.9
# Purpose 
This library takes a list of users and assigns them to other users. Consider prior exchanges and custom restrictions. 

Example uses:
1. Art Trade
2. Gift Exchange for a holiday or event

Handles various object types for User by allowing for lambda funtions to:
- 

Methods to customize user combinations:
1. No closed pairings. (currently not editable)
    - Example of a closed pair: A gets assigned B, but B is also assigned to A. 
2. Accounts for prior Trades
    - Ensure that each user gets assigned to someone they haven't been assigned to for a while. 
3. Custom restrictions 
    - By providing a custom function, you can set restrictions. 
        - Example: no user can be assigned someone on the same team.
            ```
            lambda x, y : x.team == y.team
            ```

# Outside of Scope 
- Adding the New Assignments to History
    - Allows approval or rejection to be handled by the outside of this library.
    - Otherwise it could be confusing to read and understand the error code(s) and make a decision to keep the changed history or remove the newly added Assignments
- Managing assignment history
	- Such as, updating user unique ID's across multiple assignment periods
 
# Input 
## 1. <span style="color:salmon">users</span>
- Status: Required
- What is it: 
    - List of unique objects of users
- These parameters use this one in their calculations: 
    - <span style="color:salmon">f_uniqueID</span>
    - <span style="color:salmon">f_compatibility</span>
    - <span style="color:salmon">f_restriction</span>

## 2. <span style="color:salmon">history</span> 
- Status: Optional
    - Default value: Null
- What is it: 
  - List of dictionaries, representing previous assignment results.
    	- First item (index=0) being the most recent assignment.
    	- Both the key and value in the Dictionary represent the output of FUNC_UNIQUE_ID
    	- Key_user is who was assigned the value_user
  - Assignments are stored by "trade" instead of each users' individual history so we can look at individual trade results. We lose that information when only storing a user's assignment history.
- Expected to work with these paramerts: 
    - <span style="color:salmon">f_uniqueID</span> 

## 3. <span style="color:salmon">historyLimit</span>
- Status: Optional
    - Default value: Null
- What is it: 
    - Positive int. A user cannot be assigned with someone ther've been assigned with the last times. Outside of this X value, assignments are "weighted", meaning that a user is with the person they've been assigned with the LEAST. When there is a tie... idk

## 4. <span style="color:salmon">f_uniqueID</span>
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

## 5. <span style="color:salmon">f_compatibility</span>
- Status: Optional
    - Default value: Null
- What is it: 
    - Lambda function: calculates the likelyhood a user should be assigned to another.
        - output: a number, bigger = "more likely" to assign
    - Example: 
		```
		f_compatibility = lambda x, y : abs(x.age - y.age)
		compatibility = f_compatibility(user_a, user_b)
		```

## 6. <span style="color:salmon">f_restriction</span>
- Status: Optional
    - Default value: Null
- What is it: 
    - Lambda function: 
        - compares two users and returns True or False if the Assignment is restricted. 
        - input: user objects
        - output: boolean
    - Example: 
		```
		f_restriction = lambda x, y : x.team == y.team
		is_restricted = f_restriction(user_a, user_b)
		```

## 7. <span style="color:salmon">minUsers</span> 
- Status: Optional
    - Default value: 3
- What is it: an int which checks for the minimum number of users needed for the trade.

## 8. <span style="color:salmon">maxUsers</span>
- Status: Optional
    - Default value: 50
- What is it: an int which checks for the maximum number of users needed for the trade.

# Output 
1. dictionary of assignments = 
    - both key and value are a user_unique_id,
    - key is a user, and the value is the user they are assigned.
2. error_code
    -   Type: int
    -   Values: 
        -   0: no error
        -   1: parameter error
        -   2: no possible assignment configurations given the parameters
3. errors = str. Describes any errors that the program ran into. Most errors stop the program from completing. 

# Future Feature Ideas
These are features I'd like to implement in future versions of the code
1. Change the assignment formula away from recurssion. which has a limit of 1000 recursions, and probably not the most memory friendly.
2. Exchange History
    - Toggle history building method
        1. the last X trades (current default)
        2. the last X trades the user was a part of
    - Toggle Fall back History: if no matches are found when limiting history reduce the limit and try again.
        - Ex: Fails to assign using "last 5 times" let's try the "last 4 times"
    - Possibly remove from the Gift_Exchange function, but keep in library for use with the <span style="color:salmon">f_restriction</span> parameter.
3. Have fall back Restriction calculations, in case no assignment configurations can be found with the current restrictions.
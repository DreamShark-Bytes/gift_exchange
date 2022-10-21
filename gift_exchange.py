from random import shuffle
import copy
import logging
logging.basicConfig(level=logging.WARNING, encoding='utf-8')

class ValidationError(Exception):
	def __init__ (self, message="General validation error"):
		self.message = message
		super().__init__(self.message)

class ResultError(Exception):
	def __init__ (self):
		self.message = "Error: no assignment combinations found."
		super().__init__(self.message)


def ValidateParameters(
		users, 
		history, 
		historyLimit,
		f_uniqueID, 
		f_compatibility, 
		f_restriction,
		minUsers,
		maxUsers,
		):
	errors = ""
	stop = False
	numberTypes = (int, float, complex)

	# --------------------------------------------------------------------
	# Validating Parameters for USERS
	#	- Unique items that have the minimum number of items and don't 
	#		exceed the maximum
	#	- Provided functions work
	#		- find a user's uniqueID
	
	if not isinstance(users,list):
		errors = "Parameter, users, must be a list"
		return errors

	if not isinstance(minUsers, int): 
		errors += "\n" + f"Parameter, minUsers, must be an Integer"
	elif len(users) < minUsers:
		errors += "\n" + f"There must be least {minUsers} users."
	
	if not isinstance(maxUsers, int): 
		errors += "\n" + f"Parameter, maxUsers, must be an Integer"
	elif len(users) > maxUsers:
		errors += "\n" + f"The max number of users is {maxUsers}."

	if callable(f_uniqueID) and f_uniqueID.__name__ == "<lambda>":
		try:
			userIDs = [f_uniqueID(x) for x in users]
			if len(set(userIDs)) != len(userIDs): 
				errors += "\n" + "List of Users must be unique by ID."
		except Exception as e: 
			errors += ("\n" + "Function f_uniqueID encounters error when " 
					+ f"getting ID's. Error is: {e}"
					)
			return errors[1:] # Remove leading new-line
	else:
		errors += "\n" + "Parameter, f_uniqueID, must be a lambda function"
		return errors[1:] # Remove leading new-line
	
	# --------------------------------------------------------------------
	# Validating user HISTORY 
	if history:
		if isinstance(history, list):
			assignment_history = history[0]
			if isinstance(assignment_history, dict):
				key = list(assignment_history.keys())[0]
				value = assignment_history[key]
				try:
					temp = key == value
				except Exception as e:
					errors += "\n" + "Unable to compare users in History"
			else:
				errors += "\n" + "Parameter, history, must be a list of dictionaries"
		else: 
			errors += "\n" + "Parameter, history, must be a list of dictionaries"
	if not isinstance(historyLimit, int): 
		errors += "\n" + f"Parameter, historyLimit, must be an Integer"
	# --------------------------------------------------------------------
	# Validating Parameters for the FUNCTIONS (start with "f_")
	# 	- can get a user's compatibility for assignment
	#	- can restrict a user properly from being assigned to another
	if f_restriction:
		if callable(f_restriction) and f_restriction.__name__ == "<lambda>":
			try:
				temp_restriction = f_restriction(users[0], users[1])
				if not isinstance(temp_restriction, bool): 
					errors += "\n" + "The Result of f_restriction, must be a boolean"
			except Exception as e: 
				errors += "\n" + "Function f_restriction encounters error when " 
						
		else:
			errors += "\n" + "Parameter, f_restriction, must be a lambda function"
	
	if f_compatibility:
		if callable(f_compatibility) and f_compatibility.__name__ == "<lambda>":
			try:
				temp_compatibility = f_compatibility(users[0], users[1])
				if not isinstance(temp_compatibility, numberTypes): 
					errors += "\n" + "The Result of f_compatibility, must be a number"
			except: 
				errors += ("\n" + "Function f_compatibility encounters error when "
						+ f"running, error is: {e}"
						)
		else:
			errors += "\n" + "Parameter, f_compatibility, must be a lambda function"
	
	return errors[1:] # Remove leading new-line
	


# Current users are treated as an INT representing the INDEX they are in the 
# current list of usersLeft. Historic users are matched by comparing user 
# ID's. aka some unique way to identify the user
def GiftExchange (
		users, 
		history=[], 
		historyLimit=0, 
		f_uniqueID=lambda x: x,
		f_compatibility=None,
		f_restriction=None,
		minUsers=3,
		maxUsers=50,
		):
	# validate input---------------------------------------------
	errors = ValidateParameters(**locals())

	if errors:
		raise ValidationError(errors)
	
	#------------------------------------------------------------
	# User Focused:
	# 	Tracks the history of the user for the times they participated.
	#	This ignores trades where that user didn't join.
	# Assignment Focused:
	#	If a user doesn't join, that still counts towards their 
	#	historical assignments
	focus_options = ['user', 'assignment']
	historyFocus = 'user'
	
	# Create a list of empty lists, one for each user to represent their
	# prior trades. 
	giverHistory = [ [] for _ in enumerate(users) ]
	userIDs = [f_uniqueID(x) for x in users]
	giversNeedingHistory = userIDs

	if historyLimit >0:
		for i_hist,old_assignments in enumerate(history):
			for i_user, userID in enumerate(userIDs):
				if (
						historyFocus == 'user' 
						and userID not in giversNeedingHistory
					):
					continue

				if userID in old_assignments.keys():
					# Check if the recipient of the trade is in the current 
					# list of users 
					recipientID = old_assignments[userID]
					try: 
						recipient_in_current_users = userIDs.index(recipientID)
					except:
						recipient_in_current_users = None
					giverHistory[i_user].append(recipient_in_current_users)
					if (
							historyFocus == 'user' 
							and len(giverHistory[i_user]) >= historyLimit
						):
						giversNeedingHistory.remove(userID)
				elif historyFocus == 'assignment':
					giverHistory[i_user].append(None)
			if historyFocus == 'user':
				counts = [len(x) >= historyLimit-1 for x in giverHistory]
				if all(counts):
					break 
			elif historyFocus == 'assignment' and i_hist >= historyLimit-1 :
				break
	
	#------------------------------------------------------------
	# ex: assignedUser[0] = 3, means 1st user is assigned to the 4th user
	# value meaning: 
	#		None = it has no assigned partner yet
	assignedUsers = []
	assignedUsers = [None] * len(users)
	
	givingUsersLeft = list(range(0,len(users)))
	shuffle(givingUsersLeft)
	
	receiverUsersLeft = list(range(0,len(users)))
	shuffle(receiverUsersLeft)
	
	if f_restriction:
		preprocessed_results = Assigning(assignedUsers, givingUsersLeft, giverHistory, f_restriction, users)
	else:
		preprocessed_results = Assigning(assignedUsers, givingUsersLeft, giverHistory)
	
	#------------------------------------------------------------
	# This Error will only occur when taking into account: 
	#		not assigning users if they've been assigned previously
	if preprocessed_results == None:
		raise ResultError
	logging.info(f' Final Results (user indexes) -  {preprocessed_results}')
	results = {}
	for giverIndex, recieverIndex in enumerate(preprocessed_results):
		giver_UniqueID =  f_uniqueID(users[giverIndex])
		reciever_UniqueID = f_uniqueID(users[recieverIndex])
		results[giver_UniqueID] = reciever_UniqueID
	return results

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------

# Recursive function to find a good assignments
def Assigning(assignedUsers, givingUsersLeft, giverHistory, f_restriction=None, users=None):
	result = None
	newList = givingUsersLeft[1:]
	giver = givingUsersLeft[:1][0]
	# giver = newList.pop(0)
	
	giverCount = len(assignedUsers) - len(newList)
	for receiver in range(len(assignedUsers)):
		logging.info(f' #{giverCount} - Attempting g{giver}:r{receiver} -- NL{newList}') 
		if (
			receiver in assignedUsers # Receiver is already assigned to someone
			or receiver == giver # Giver and receiver must not be the same user
			or assignedUsers[receiver] == giver # No closed loop between giver and receiver
			or receiver in giverHistory[giver] # Receiver is not part of the currated Giver History
		): 
			logging.info(f' #{giverCount} - SKIPPING Receiver index {receiver} - one of multiple possibilities')
			continue
		
		if f_restriction:
			giver_user = users[giver]
			receiver_User = users[receiver]
			if f_restriction(giver_user, receiver_User):
				logging.info(f' #{giverCount} - SKIPPING Receiver index {receiver} - restricted')
				continue
		
		assignedUsers[giver] = receiver
		logging.info(f' #{giverCount} - ASSIGNING Receiver  g{giver}:r{receiver}, current assignments: {assignedUsers}')
		
		if len(newList) == 0: 
			return assignedUsers
		result = Assigning(assignedUsers, newList, giverHistory, f_restriction, users)
		if result: 
			return result
		else:
			assignedUsers[giver] = None
	logging.info(f' Giving up on - Giver #{giverCount}')
	return result

def GiftExchange2 (
		users, 
		history=[], 
		historyLimit=0, 
		f_uniqueID=lambda x: x,
		f_compatibility=None,
		f_restriction=None,
		minUsers=3,
		maxUsers=50,
		):
	# validate input---------------------------------------------
	errors = ValidateParameters(**locals())

	if errors:
		raise ValidationError(errors)
	
	#------------------------------------------------------------
	# User Focused:
	# 	Tracks the history of the user for the times they participated.
	#	This ignores trades where that user didn't join.
	# Assignment Focused:
	#	If a user doesn't join, that still counts towards their 
	#	historical assignments
	focus_options = ['user', 'assignment']
	historyFocus = 'user'
	
	# Create a list of empty lists, one for each user to represent their
	# prior trades. 
	giverHistory = [ [] for _ in enumerate(users) ]
	userIDs = [f_uniqueID(x) for x in users]
	giversNeedingHistory = userIDs

	if historyLimit >0:
		for i_hist,old_assignments in enumerate(history):
			for i_user, userID in enumerate(userIDs):
				if (
						historyFocus == 'user' 
						and userID not in giversNeedingHistory
					):
					continue

				if userID in old_assignments.keys():
					# Check if the recipient of the trade is in the current 
					# list of users 
					recipientID = old_assignments[userID]
					try: 
						recipient_in_current_users = userIDs.index(recipientID)
					except:
						recipient_in_current_users = None
					giverHistory[i_user].append(recipient_in_current_users)
					if (
							historyFocus == 'user' 
							and len(giverHistory[i_user]) >= historyLimit
						):
						giversNeedingHistory.remove(userID)
				elif historyFocus == 'assignment':
					giverHistory[i_user].append(None)
			if historyFocus == 'user':
				counts = [len(x) >= historyLimit-1 for x in giverHistory]
				if all(counts):
					break 
			elif historyFocus == 'assignment' and i_hist >= historyLimit-1 :
				break
	
	#------------------------------------------------------------
	# ex: assignedUser[0] = 3, means 1st user is assigned to the 4th user
	# value meaning: 
	#		None = it has no assigned partner yet
	assignedUsers = []
	assignedUsers = [None] * len(users)
	
	givingUsersLeft = list(range(0,len(users)))
	shuffle(givingUsersLeft)
	
	receiverUsersLeft_originalOrder = list(range(0,len(users)))
	shuffle(receiverUsersLeft_originalOrder)
	receiverUsersLeft = copy.copy(receiverUsersLeft_originalOrder)

	escapable = False
	solutionFound = False
	receiversExhausted = True
	while not escapable: 
		if receiversExhausted:
			giver = givingUsersLeft.pop(0)
			receiversExhausted = False
		receiver = receiverUsersLeft.pop(0)

		giverCount = len(assignedUsers) - len(givingUsersLeft)
		logging.info(f' #{giverCount} - Attempting g{giver}:r{receiver} -- NL{givingUsersLeft}') 
		if (
			receiver in assignedUsers # Receiver is already assigned to someone
			or receiver == giver # Giver and receiver must not be the same user
			or assignedUsers[receiver] == giver # No closed loop between giver and receiver
			or receiver in giverHistory[giver] # Receiver is not part of the currated Giver History
		): 
			logging.info(f' #{giverCount} - SKIPPING Receiver index {receiver} - one of multiple possibilities')
			continue
		
		if f_restriction:
			giver_user = users[giver]
			receiver_User = users[receiver]
			if f_restriction(giver_user, receiver_User):
				logging.info(f' #{giverCount} - SKIPPING Receiver index {receiver} - restricted')
				continue
		
		assignedUsers[giver] = receiver
		receiversExhausted = True

		logging.info(f' #{giverCount} - ASSIGNING Receiver  g{giver}:r{receiver}, current assignments: {assignedUsers}')
		logging.info(f'\t Giving Users Left: {givingUsersLeft}')
		logging.info(f'\t Assigned Users Left: {receiverUsersLeft}')
		logging.info(f'\t Assigned Users Left ORIGINAL: {receiverUsersLeft_originalOrder}')
		
		if len(receiverUsersLeft) == 0: 
			if len(givingUsersLeft) == 0:
				if None in assignedUsers:
					solutionFound = False
					raise ResultError
				else:
					solutionFound = True
				escapable = True
			else:
				receiverUsersLeft = copy.copy(receiverUsersLeft_originalOrder)
				logging.info(f' Giving up on - Giver #{giverCount}')

	#------------------------------------------------------------

	logging.info(f' Final Results (user indexes) -  {assignedUsers}')
	results = {}
	for giverIndex, recieverIndex in enumerate(assignedUsers):
		giver_UniqueID =  f_uniqueID(users[giverIndex])
		reciever_UniqueID = f_uniqueID(users[recieverIndex])
		results[giver_UniqueID] = reciever_UniqueID
	return results

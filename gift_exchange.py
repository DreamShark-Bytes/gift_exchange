from random import shuffle, random
import copy
import logging
logging.basicConfig(level=logging.WARNING, encoding='utf-8')
ordinal = lambda n: '%d%s' % (n,'tsnrhtdd'[(n//10%10!=1)*(n%10<4)*n%10::4])

class ValidationError(Exception):
	def __init__ (self, message='General validation error'):
		self.message = message
		super().__init__(self.message)

class ResultError(Exception):
	def __init__ (self):
		self.message = 'Error: no assignment combinations found.'
		super().__init__(self.message)

# Reference:
# http://utopia.duth.gr/~pefraimi/research/data/2007EncOfAlg.pdf
# implementation speed: O(n log(n))
def weighted_shuffle(items, weights):
	# NOT reversing the sort to align with my definition of "heavier = more likely"
	# This is because of the way that the formula calculates likelyhood.
	#	Lower numbers are almost always at the forefront, 
	# 	while things even out after that first quartile
	order = sorted(range(len(items)), key=lambda i: random() ** (1.0 / weights[i]) if weights[i] > 0 else 0, reverse=False)
	return [items[i] for i in order]

# Validate the paramters of the gift_exchange function are in working order
def ValidateParameters(
		users, 
		f_uniqueID,
		history, 
		historyLimit,
		history_ParticipationRequired,
		f_compatibility, 
		f_restriction,
		minUsers,
		maxUsers,
		):
	errors = ''
	stop = False
	numberTypes = (int, float, complex)

	# --------------------------------------------------------------------
	# Validating Parameters for USERS
	#	- List of users 
	#	- Users are Unique, by the provided f_uniqueID lambda
	#	- minUsers and maxUsers are abided by
	
	
	if not isinstance(users,list):
		errors = 'Parameter, users, must be a list'
		return errors

	if not isinstance(minUsers, int): 
		errors += '\n' + f'Parameter, minUsers, must be an Integer'
	elif len(users) < minUsers:
		errors += '\n' + f'There must be least {minUsers} users.'
	
	if not isinstance(maxUsers, int): 
		errors += '\n' + f'Parameter, maxUsers, must be an Integer'
	elif len(users) > maxUsers:
		errors += '\n' + f'The max number of users is {maxUsers}.'

	if callable(f_uniqueID) and f_uniqueID.__name__ == '<lambda>':
		try:
			userIDs = [f_uniqueID(x) for x in users]
			if len(set(userIDs)) != len(userIDs): 
				errors += '\n' + 'List of Users must be unique by ID.'
		except Exception as e: 
			errors += ('\n' + 'Function f_uniqueID encounters error when ' 
					+ f'getting IDs. Error is: {e}'
					)
			return errors[1:] # Remove leading new-line
	else:
		errors += '\n' + 'Parameter, f_uniqueID, must be a lambda function'
		return errors[1:] # Remove leading new-line
	
	# --------------------------------------------------------------------
	# Validating user HISTORY parameters
	#	- history variable
	#	- historyLimit
	#	- history_ParticipationRequired
	if history:
		if isinstance(history, list):
			assignment_history = history[0]
			if isinstance(assignment_history, dict):
				key = list(assignment_history.keys())[0]
				value = assignment_history[key]
				try:
					temp = key == value
				except Exception as e:
					errors += '\n' + 'Unable to compare users in History'
			else:
				errors += '\n' + 'Parameter, history, must be a list of dictionaries'
		else: 
			errors += '\n' + 'Parameter, history, must be a list of dictionaries'
	if not isinstance(historyLimit, int): 
		errors += '\n' + f'Parameter, historyLimit, must be an Integer'

	if not isinstance(history_ParticipationRequired, bool):
		errors += '\n' + 'Parameter, history_ParticipationRequired, must be a Boolean'
	# --------------------------------------------------------------------
	# Validating Parameters for the FUNCTIONS (start with "f_")
	# 	- can get a user's compatibility for assignment
	#	- can restrict a user properly from being assigned to another
	if f_restriction:
		if callable(f_restriction) and f_restriction.__name__ == '<lambda>':
			try:
				temp_restriction = f_restriction(users[0], users[1])
				if not isinstance(temp_restriction, bool): 
					errors += '\n' + 'The Result of f_restriction, must be a boolean'
			except Exception as e: 
				errors += '\n' + 'Function f_restriction encounters error when ' 
						
		else:
			errors += '\n' + 'Parameter, f_restriction, must be a lambda function'
	
	if f_compatibility:
		if callable(f_compatibility) and f_compatibility.__name__ == '<lambda>':
			try:
				temp_compatibility = f_compatibility(users[0], users[1])
				if not isinstance(temp_compatibility, numberTypes): 
					errors += '\n' + 'The Result of f_compatibility, must be a number'
			except: 
				errors += ('\n' + 'Function f_compatibility encounters error when '
						+ f'running, error is: {e}'
						)
		else:
			errors += '\n' + 'Parameter, f_compatibility, must be a lambda function'
	
	return errors[1:] # Remove leading new-line
	

def GiftExchange (
		users, 
		f_uniqueID=lambda x: x,
		history=[], 
		historyLimit=0, 
		history_ParticipationRequired=False,
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
	# history_ParticipationRequired == TRUE, exchange focused
	#	Regardless of a user's participation in prior Exchanges
	#	the historyLimit relates to the number of exchanges that occurred
	# history_ParticipationRequired == FALSE, user focused
	# 	Tracks the history of the user ONLY for the times they participated.
	#	Meaning user's who don't participate often are still 
	#	not assigned people they've given to in the last X exchanges
	#	where x == historyLimit
	
	# Create a list of empty lists, one for each user to represent their
	# prior trades. 
	giverHistory = [ [] for _ in enumerate(users) ]
	
	if historyLimit >0:
		# Dictionary of users in current exchanges
		#	key = index of that user in Users parameter
		#	value = the user's uniqueID
		giversNeedingHistory = dict((i,f_uniqueID(v)) for i, v in enumerate(users))

		userIDs = [ f_uniqueID(x) for x in users ]
		# giversNeedingHistory = userIDs.copy()

		logging.info(' ----- Building History')
		for i_hist, historicExchange in enumerate(history):
			logging.info(f' -- Exchange [{i_hist}] : {historicExchange}')
			for i_user in list(giversNeedingHistory): # Get's the dict keys
				
				# Doing this instead of Enumerate because we're changing
				#	the size of the dictionary mid-iteration, which 
				#	causes an error otherwise
				userID = giversNeedingHistory[i_user]
				logging.info(f'checking user {userID=}, inx={i_user}') 
				if userID in historicExchange.keys():
					# Check if the recipient of the trade is in the current 
					# list of users 
					recipientID = historicExchange[userID]
					try: 
						recipient_in_current_users = userIDs.index(recipientID)
						logging.info(f'checking user {userID=}, inx={i_user}') 
					except:
						recipient_in_current_users = None
					giverHistory[i_user].append(recipient_in_current_users)
				elif not history_ParticipationRequired:
					giverHistory[i_user].append(None)
				
				if len(giverHistory[i_user]) >= historyLimit:
					giversNeedingHistory.pop(i_user)
			if not giversNeedingHistory:
				break
	
	#------------------------------------------------------------
	# ex: assignedUser[0] = 3, means 1st user is assigned to the 4th user
	# value meaning: 
	#		None = it has no assigned partner yet
	assignedUsers = []
	assignedUsers = [None] * len(users)
	
	givers = list(range(0,len(users)))
	shuffle(givers)
	logging.info(f' ----- GIVER ORDER: {givers}')

	# List
	# - the list index matches that of the index of a giver in the list of Users
	# - each item in this list, is a randomized list of receivers (their index in the list of Users)
	if f_compatibility:
		# make empty multi-dimensional array
		receivers_byGiver = [ [] for _ in range(len(users))] 
		weights_byGiver = [ [] for _ in range(len(users))] 
		for i in range(len(users)):
			giver_user = users[i]
			weights_of_current_giver = [ f_compatibility(giver_user, users[receiver]) for receiver in range(len(users))]
			# Bigger = more likely (heavier weight)
			receivers_byGiver[i] = weighted_shuffle(range(len(users)), weights_of_current_giver)
			weights_byGiver[i] = weights_of_current_giver
	else:
		receivers_byGiver = [ sorted( range(len(users)), key=lambda k: random()) for x in range(len(users)) ]

	logging.info(f' ----- RECEIVER ORDERS: {receivers_byGiver}')
	# Dictionary 
	# - Index = Index of user that is the giver
	# - value = keeping track of number of Receivers we've tried so far. Used as Index in receivers_byGiver[key/givgiversAssigneder]
	attemptTracking = [-1] * len(users) # dict.fromkeys(list(range(0,len(users))), 0)
	logging.info(f' ----- PRE-PROCESSED ATTEMPT COUNTS: {attemptTracking}')

	# initialize
	escapable = False
	receiversExhausted = True
	initialize_Exchange = True
	givingUsers_Index = -1 
	giver = givers[0] 
	receiverAttempt = attemptTracking[giver]
	receiver = receivers_byGiver[giver][receiverAttempt]

	while not escapable: 
		# Putting this check here for the case of Skips
		# --------------------------------------------------
		# the number of givers used matches the count of total users
		if None not in assignedUsers:
			escapable = True
			continue
		if givingUsers_Index <= 0: # index compared to count
			if not receiversExhausted:
				# if the number of attempts for this Giver matches the count of total users
				if attemptTracking[giver] >= len(users) - 1: # index compared to count
					raise ResultError
					escapable = True
					continue
		# well, the attempts of Receivers has 
		elif attemptTracking[giver] >= len(users) - 1: # index compared to count
			if not receiversExhausted:
				logging.info(f' Giving up on - Giver #{givingUsers_Index + 1} as {giver}\n')
				
				# Reset count of Receivers tried for this level of Giver
				attemptTracking[giver] = -1
				assignedUsers[giver] = None

				# Minusing 2 since we'll be adding 1 before re-assigning 'giver'
				givingUsers_Index -= 2 
				
				receiversExhausted = True

		if receiversExhausted:
			givingUsers_Index += 1
			giverAttempt_orginal = ordinal(givingUsers_Index + 1)
			giver = givers[givingUsers_Index]
			givingUsersLeft = sorted(givers[givingUsers_Index + 1:])
			receiversExhausted = False

		# This is in case we gave up on a Giver, but the previous giver was also at it's max
		if attemptTracking[giver] >= len(users) - 1:
			continue
		attemptTracking[giver] += 1
		receiverAttempt = attemptTracking[giver]
		receiverAttempt_ordinal = ordinal(receiverAttempt + 1)
		receiver = receivers_byGiver[giver][receiverAttempt]
		receivingUsersLeft = sorted(receivers_byGiver[giver][receiverAttempt + 1:])

		logging.info(f' current attemtps counters {attemptTracking}') 
		logging.info(f' {giverAttempt_orginal}:{receiverAttempt_ordinal} - Attempting g{giver}:r{receiver} -- GL{givingUsersLeft}:RL{receivingUsersLeft}') 

		if receiver in assignedUsers:
			logging.info(f' {giverAttempt_orginal} G - SKIPPING Receiver index {receiver} - Receiver is already assigned to someone')
			continue
		elif assignedUsers[receiver] == giver:
			logging.info(f' {giverAttempt_orginal} G - SKIPPING Receiver index {receiver} - Creates closed loop')
			continue
		elif receiver == giver:
			logging.info(f' {giverAttempt_orginal} G - SKIPPING Receiver index {receiver} - Giver and receiver must not be the same user')
			continue
		elif receiver in giverHistory[giver]:
			logging.info(f' {giverAttempt_orginal} G - SKIPPING Receiver index {receiver} - Receiver is restricted via Giver History Limit')
			continue
		elif f_restriction:
			giver_user = users[giver]
			receiver_User = users[receiver]
			if f_restriction(giver_user, receiver_User):
				logging.info(f' {giverAttempt_orginal} G - SKIPPING Receiver index {receiver} - restricted')
				continue
		
		assignedUsers[giver] = receiver
		receiversExhausted = True
		logging.info(f' {giverAttempt_orginal} G - ASSIGNING Receiver  g{giver}:r{receiver}, current assignments: {assignedUsers}\n')

	#------------------------------------------------------------

	logging.info(f' Final Results (user indexes) -  {assignedUsers}')
	results = {}
	for giverIndex, recieverIndex in enumerate(assignedUsers):
		giver_UniqueID =  f_uniqueID(users[giverIndex])
		reciever_UniqueID = f_uniqueID(users[recieverIndex])
		results[giver_UniqueID] = reciever_UniqueID
	return results

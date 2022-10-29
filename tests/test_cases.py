import unittest
from gift_exchange import *
import time

ordinal = lambda n: '%d%s' % (n,'tsnrhtdd'[(n//10%10!=1)*(n%10<4)*n%10::4])

class example_User():
	def __init__(self, id, name='', team=''):
		self.id = id
		self.name = name
		self.team = team

test_userA = example_User(id=0, name='A', team='red')
test_userB = example_User(id=1, name='B', team='blue')
test_userC = example_User(id=2, name='C', team='blue')
test_users = [test_userA, test_userB, test_userC]

# Note: only ID's: 0, 1, 2 and 3 (later) are used in testing
# Currently no "history validation" functions are used
test_user_history = [
	{0:1, 9:9},
	{1:2, 9:9},
	{2:0, 9:9},
	{9:9},
	{9:9}
]

sufficient_test_count = 1000

# This method compares two dictionaries to make sure they are "the same"
# Since I can't compare two dictionaries using the __equals__ dunder method
def DictDiffTest(dict1, dict2):
	if len(dict1) != len(dict2):
		return False
	output = True
	try:
		for key, value in dict1.items():
			if dict1[key] != dict2[key]:
				output = False
	except Exception as e:
		print(f'ERROR: {e}')
		output = False
	return output

# Reference:
# https://stackoverflow.com/questions/12627118/get-a-function-arguments-default-value
import inspect
def get_default_args(func):
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }
defaults = get_default_args(GiftExchange)

# Before we start to do real processing (to find assignments)
# the program validates the parameters given to it
# these tests are restricted to that part of the code
class Test_Validation(unittest.TestCase):
	def test_parameter_type_users(self):
		with self.assertRaises(ValidationError):
			results = GiftExchange(4)

	def test_parameter_type_other(self): 
		users = ['a','b','c']
		# Asserting that no error is thrown with example users 
		# so we can use them later
		try:
			results = GiftExchange(users)
		except Exception as e:
			self.fail('Function, unable to process basic user list,'
				+ f' {users}, using default parameters without'
				+ ' raising an exception'
				)

		with self.assertRaises(
				ValidationError, 
				msg='parameter error: "minUsers"'
					+ ' - must only accept object type: int'
				):
			results = GiftExchange(users, minUsers='weh')

		with self.assertRaises(
				ValidationError,
				msg='parameter error: "maxUsers"'
					+ ' - must only accept object type: int'
				):
			results = GiftExchange(users, maxUsers='weh')

		with self.assertRaises(
				Exception, 
				msg='parameter error: "history"'
					+ ' - must only accept object type: list'
				):
			results = GiftExchange(users, history='weh')

		with self.assertRaises(
				Exception, 
				msg='parameter error: "historyLimit"'
					+ ' - must only accept object type: int'
				):
			results = GiftExchange(users, historyLimit='weh')
		
		with self.assertRaises(
				Exception, 
				msg='parameter error: "f_uniqueID"'
					+ ' - must only accept object type: lambda'
				):
			results = GiftExchange(users, f_uniqueID='weh')
		
		with self.assertRaises(
				Exception, 
				msg='parameter error: "f_uniqueID"'
					+ ' - must only accept object type: lambda'
				):
			results = GiftExchange(users, f_compatibility='weh')
		
		with self.assertRaises(
				Exception, 
				msg='parameter error: "f_uniqueID"'
					+ ' - must only accept object type: lambda'):
			results = GiftExchange(users, f_restriction='weh')

	def test_minUsers(self):
		try:
			default_minUsers = defaults['minUsers']
		except: 
			# Dictionary Key error
			self.fail('minUsers needs a Default value')

		with self.assertRaises(
				Exception, 
				msg=f'there must be at least {default_minUsers} users provided'
					+' (default minUsers value)'
				):
			results = GiftExchange(['a','b'])

	def test_minUsers2(self):
		with self.assertRaises(
				Exception, 
				msg='failed to recognize that the number of users'
					+ ' does not meet a provided minUsers threshold'
				):
			results = GiftExchange(['a','b','c'], minUsers = 5)

	def test_maxUsers(self):
		try:
			default_maxUsers = defaults['maxUsers']
		except: 
			# Dictionary Key error
			self.fail('maxUsers needs a Default value')

		with self.assertRaises(
				Exception, 
				msg='failed to recognize that the number of users'
					+ f' exceeds {default_maxUsers} (default maxUsers value)'
				):
			results = GiftExchange(list(range(100)))
	
	def test_maxUsers2(self):
		with self.assertRaises(
				Exception, 
				msg='failed to recognize that the number of users exceeds a'
					+ ' provided maxUsers threshold'
				):
			results = GiftExchange(list(range(10)), maxUsers=5)
		
	def test_unique_users(self):
		try:
			default_value = defaults['f_uniqueID']
			# make lambda function readable
			# strip() b/c there is weird whitespace on either side
			# [:-1] = Removes trailing comma
			default_value = str(inspect.getsource(default_value)).strip()[:-1]
		except: 
			# Dictionary Key error
			self.fail('f_uniqueID needs a Default value')

		users = ['a','b','c', 'c']

		with self.assertRaises(
				Exception, 
				msg=f'failed to recognize that the provided users, {users}, is not a'
					+ f' unique list (using default {default_value})'
				):
			results = GiftExchange()
	
	def test_f_uniqueID(self):
		with self.assertRaises(
				Exception, 
				msg='failed to recognize that the provided users objects,'
					+ ' type=ExampleUser, is not a unique list'
					+ ' (using f_uniqueID=lambda x: x.team)'
				):
			results = GiftExchange(test_users, f_uniqueID=lambda x: x.team)

class Test_Processing(unittest.TestCase):
	def test_user_combinations(self):
		temp_users = ['a','b','c']
		for i in range(sufficient_test_count):
			results = GiftExchange(temp_users)
			if results['a'] == 'b':
				test_against = {'a':'b', 'b':'c', 'c':'a'}
			else: # a:c is in results
				test_against = {'a':'c', 'b':'a', 'c':'b'}
			self.assertTrue(
				DictDiffTest(results, test_against),
				msg=f'basic user list, {temp_users}, assignment returned an'
					+ f' impossible combination: {results}'
				)

	def test_user_history(self): 
		for i in range(sufficient_test_count):
			# example_User(id=0, name="A", team="red")
			# example_User(id=1, name="B", team="blue")
			# example_User(id=2, name="C", team="blue")
			results = GiftExchange(
				test_users, 
				history=test_user_history, 
				historyLimit=1,
				history_ParticipationRequired=True,
				f_uniqueID=lambda x: x.id
				)
			self.assertTrue(
				DictDiffTest(results, {0:2,1:0,2:1}),
				#			solution   [ 2, 0, 1 ]
				# 		 	history	   [ 1, 2, 0 ] or {0:1,1:2,2:0}
				msg=' User History failure (Participation Required)'
					+ ' - Unable to find the only assignment combination,'
					+ ' given the users and history '
				)

	def test_user_history2(self):
		for i in range(sufficient_test_count):
			# example_User(id=0, name='A', team='red'')
			# example_User(id=1, name='B', team='blue')
			# example_User(id=2, name='C', team='blue')
			results = GiftExchange(
				test_users, 
				history=test_user_history, 
				historyLimit=3,
				history_ParticipationRequired=False,
				f_uniqueID=lambda x: x.id
				)
			self.assertTrue(
				DictDiffTest(results, {0:2,1:0,2:1}),
				#			solution   [ 2, 0, 1 ]
				# 		 	history	   [ 1, 2, 0 ] or {0:1,1:2,2:0}
				msg=' User History failure (Participation NOT Required)'
					+ ' - Unable to find the only assignment combination,'
					+ ' given the users and history '
				)
	# Making sure history doesn't play a part when the default 
	# historyLimit should be 0
	def test_user_history3(self): 
		try:
			default_value = defaults['historyLimit']
		except: 
			# Dictionary Key error
			self.fail('historyLimit needs a Default value')

		if default_value != 0:
			self.fail('historyLimit default value must be 0')

		temp_users = ['a','b','c']
		temp_history = {'a':'c','b':'a','c':'b'}
		for i in range(sufficient_test_count):
			results = GiftExchange(
				users = temp_users, 
				history=test_user_history
				)
			# All 3 possibilities
			if results['a'] == 'b':
				test_against = {'a':'b', 'b':'c', 'c':'a'}
			else: # a:c is in results
				test_against = {'a':'c', 'b':'a', 'c':'b'}
			self.assertTrue(
				DictDiffTest(results, test_against),
				msg=' User History failure '
					+ ' - history value is impacting results when'
					+ ' default historyLimit is 0'
				)

	def test_restrictions(self):
		# 			example_User(id=0, name='A', team='red'')
		# 			example_User(id=1, name='B', team='blue')
		# 			example_User(id=2, name='C', team='blue')

		# add 4th user to list of users for this test
		test_userD = example_User(id=3, name='D', team='green')
		new_test_users = test_users + [test_userD]

		restrictionFunc_raw = lambda x, y: x.team == y.team
		restrictionFunc = str(
				inspect.getsource(restrictionFunc_raw)
			).strip()[:-1]

		for i in range(sufficient_test_count):
			results = GiftExchange(
				new_test_users, 
				f_uniqueID=lambda x: x.id, 
				f_restriction=restrictionFunc_raw
				)
			if results[0] == 1:
				test_against = {0:1, 1:3, 2:0, 3:2}
			else:
				test_against = {0:2, 1:0, 2:3, 3:1}
			self.assertTrue(
				DictDiffTest(results, test_against),
				msg='failed to properly restrict users, '
					+ f' among new_test_users, given {restrictionFunc}'
				)


class ACTIVE_TESTS(unittest.TestCase):
	def test_find_ExceptionType(self):
		try:
			nothing_here = 'nothing here'
		except Exception as e:
			template = 'An exception of type {0} occurred. Arguments:\n{1!r}'
			message = template.format(type(e).__name__, e.args)
			print(message)

	
# Defunc Tests --------------------------------------------
class STRESS_TESTS():#unittest.TestCase):
	def test_stress(self):
		# NOTES
		# using the RaspberryPi4B, 4GB memory
		#	- 3,000 users : 10 loops : full history 
		#		~64 seconds each
		#	- 3,000 users : 10 loops : full history : restrict same teams, count two 
		#		~109 seconds each (PC is ~28sec)
		print('STESS TEST TIME:')
		myHistory = []
		
		teams = ['red','blue']
		my_users = []
		user_count = 3000
		for i in range(user_count):
			user_team = teams[i%len(teams)]
			user = example_User(id=i, name=f'user_{i}', team=user_team)
			my_users.append(user)

		loop_count = 10
		print(f' -- running {user_count} users, looping {loop_count} times')
		for i in range(loop_count):
			start = time.perf_counter()
			print(f' {i+1}/{loop_count} - ATTEMPTING', end='\r')
			results = GiftExchange(
				my_users, 
				f_uniqueID=lambda x:x.id, 
				f_restriction=lambda x,y: x.team == y.team, 
				maxUsers=999999, 
				history=myHistory, 
				historyLimit=loop_count
				)
			myHistory = [results] + myHistory
			end = time.perf_counter()
			timedelta = end - start
			print(f' {i+1}/{loop_count} - COMPLETE: took {end - start:0.4f} seconds ')

class misc_tests():#unittest.TestCase):

	# Not a test I know how to compute "success" for
	# This test generates a chart, showing the distribution of weighted items
	def test_weightedShuffle_distribution(self):
		import numpy as np # Currently not used
		import matplotlib.pyplot as plt
		
		item_count = 100
		sampleSize = 5
		cycles = 5000

		list_of_items = list(range(item_count))
		# print(f'{list_of_items=}')
		list_of_weights = [ (x+1)*100 for x in list_of_items ]
		results = []
		counts = [ [ 0 for _ in range(item_count)]  for _ in  range(item_count) ]
		
		for i in range(cycles):
			temp = weighted_shuffle(list_of_items, list_of_weights)
			results.append(temp)
			for i, v in enumerate(temp):
				counts[v][i] += 1

		fig, axs = plt.subplots(sampleSize, figsize=(5,10), sharex=True, sharey=False)
		width = 0.5

		plt.suptitle(f'Distribution of Weighted Shuffle\n{item_count} items, weight=item# x 100. Ran {cycles} times')
		plt.xlabel('Placement in line')
		plt.ylabel('Count of occurences')

		sampleItems = [ list_of_items[round(x/(sampleSize-1)*item_count)] for x in list(range(sampleSize-1)) ] + [list_of_items[-1]]
		# print(f'{item_count=},{sampleItems=}')

		for i,chosen_item in enumerate(sampleItems):
			print(f'\t {i=}')
			placeInLine = list_of_items
			columns = placeInLine
			values = counts[chosen_item]

			# Add annotation to bars
			axs[i].bar(columns, values, color='blue')
			axs[i].set_title(f'item={chosen_item+1} (of {item_count}), weight={list_of_weights[chosen_item]}')

		
		
		plt.show()

if __name__ == '__main__':
    unittest.main()
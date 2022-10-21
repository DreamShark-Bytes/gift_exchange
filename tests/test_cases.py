import unittest
from gift_exchange import *

class example_User():
	def __init__(self, id, name="", team=""):
		self.id = id
		self.name = name
		self.team = team

test_userA = example_User(id=1, name="A", team="red")
test_userB = example_User(id=2, name="B", team="blue")
test_userC = example_User(id=3, name="C", team="blue")
test_users = [test_userA, test_userB, test_userC]

test_user_history = [
	{1:2,2:3,3:1}
]

sufficient_test_count = 10

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


class Test_Validation(unittest.TestCase):

	def test_parameter_type_users(self):
		with self.assertRaises(ValidationError):
			results = GiftExchange(4)

	def test_parameter_type_other(self): 
		users = ['a','b','c']
		# Asserting that no error is thrown with example users 
		# so we can use them later

		results = GiftExchange(users)

		with self.assertRaises(ValidationError):
			results = GiftExchange(users, minUsers="weh")

		with self.assertRaises(ValidationError):
			results = GiftExchange(users, maxUsers="weh")

		with self.assertRaises(Exception):
			results = GiftExchange(users, history="weh")

		with self.assertRaises(Exception):
			results = GiftExchange(users, historyLimit="weh")
		
		with self.assertRaises(Exception):
			results = GiftExchange(users, f_uniqueID="weh")
		
		with self.assertRaises(Exception):
			results = GiftExchange(users, f_compatibility="weh")
		
		with self.assertRaises(Exception):
			results = GiftExchange(users, f_restriction="weh")

	def test_minUsers(self):
		with self.assertRaises(Exception):
			results = GiftExchange(['a','b'])

	def test_minUsers2(self):
		with self.assertRaises(Exception):
			results = GiftExchange(['a','b','c'], minUsers = 5)

	def test_maxUsers(self):
		with self.assertRaises(Exception):
			results = GiftExchange(list(range(100)))
	
	def test_maxUsers2(self):
		with self.assertRaises(Exception):
			results = GiftExchange(list(range(10)), maxUsers=5)
		
	def test_unique_users(self):
		with self.assertRaises(Exception):
			results = GiftExchange(['a','b','c','c'])
	
	def test_f_uniqueID(self):
		with self.assertRaises(Exception):
			results = GiftExchange(test_users, f_uniqueID=lambda x: x.team)

class Test_Processing(unittest.TestCase):
	def test_user_combinations(self):
		for i in range(sufficient_test_count):
			results = GiftExchange(['a','b','c'])
			if results['a'] == 'b':
				test_against = {'a':'b', 'b':'c', 'c':'a'}
			else: # a:c is in results
				test_against = {'a':'c', 'b':'a', 'c':'b'}
			self.assertTrue(DictDiffTest(results, test_against))

	def test_user_history(self):
		for i in range(sufficient_test_count):
			results = GiftExchange(test_users, test_user_history, historyLimit=1, f_uniqueID=lambda x: x.id)
			self.assertTrue(DictDiffTest(results, {1:3,3:2,2:1}))
	
	
	def test_restrictions(self):
		# 			example_User(id=1, name="A", team="red")
		#			example_User(id=2, name="B", team="blue")
		#			example_User(id=3, name="C", team="blue")
		test_userD = example_User(id=4, name="D", team="green")
		new_test_users = test_users + [test_userD]
		for i in range(sufficient_test_count):
			results = GiftExchange(new_test_users, f_uniqueID=lambda x: x.id, f_restriction=lambda x, y: x.team == y.team)
			if results[1] == 2:
				test_against = {1:2, 2:4, 4:3, 3:1}
			else:
				test_against = {1:3, 3:4, 4:2, 2:1}
			self.assertTrue(DictDiffTest(results, test_against))

class bugs_that_need_fixed(): #unittest.TestCase):
	def test_user_list_too_large_for_recursion(self):
		with self.assertRaises(RecursionError):
			results = GiftExchange(list(range(1000)), maxUsers=9999)

class ACTIVE_TESTS(unittest.TestCase):
	def find_ExceptionType(self):
		try:
			nothing_here = 'nothing here'
		except Exception as e:
			template = "An exception of type {0} occurred. Arguments:\n{1!r}"
			message = template.format(type(e).__name__, e.args)
			print(message)

if __name__ == '__main__':
    unittest.main()
import unittest

from python_redux import create_store, combine_reducers
from test.helpers.action_creators import add_todo, dispatch_in_middle, throw_error, unknown_action
from test.helpers.reducers import reducers

class TestCreateStoreMethod(unittest.TestCase):
	def test_exposes_public_API(self):
		store = create_store(combine_reducers(reducers))
		methods = store.keys()
		
		self.assertEqual(len(methods), 4)
		self.assertTrue('subscribe' in methods)
		self.assertTrue('dispatch' in methods)
		self.assertTrue('get_state' in methods)
		self.assertTrue('replace_reducer' in methods)
	
	def test_throws_if_reducer_is_not_a_function(self):
		with self.assertRaises(Exception):
			create_store(combine_reducers)
		with self.assertRaises(Exception):
			create_store('test')
		with self.assertRaises(Exception):
			create_store({})
		try:
			create_store(lambda *x: {})
		except Exception as e:
			self.fail('create_store(lambda: {}) should not have failed')
	
	def test_passes_initial_action_and_initial_state(self):
		store = create_store(reducers['todos'], [
			{
				'id': 1,
				'text': 'Hello'
			}
		])
		self.assertEqual(store['get_state'](), [{ 'id': 1, 'text': 'Hello' }])
	
	def test_applies_reducer_to_previous_state(self):
		store = create_store(reducers['todos'])
		self.assertEqual(store['get_state'](), [])
		
		store['dispatch'](unknown_action())
		self.assertEqual(store['get_state'](), [])
		
		store['dispatch'](add_todo('Hello'))
		self.assertEqual(store['get_state'](), [
			{
				'id': 1,
				'text': 'Hello'
			}
		])
		
		store['dispatch'](add_todo('World'))
		self.assertEqual(store['get_state'](), [
			{
				'id': 1,
				'text': 'Hello'
			},
			{
				'id': 2,
				'text': 'World'
			}
		])
	
	def test_applied_reducer_to_initial_state(self):
		store = create_store(reducers['todos'], [
			{
				'id': 1,
				'text': 'Hello'
			}
		])
		self.assertEqual(store['get_state'](), [
			{
				'id': 1,
				'text': 'Hello'
			}
		])
		
		store['dispatch'](unknown_action())
		self.assertEqual(store['get_state'](), [
			{
				'id': 1,
				'text': 'Hello'
			}
		])
		
		store['dispatch'](add_todo('World'))
		self.assertEqual(store['get_state'](), [
			{
				'id': 1,
				'text': 'Hello'
			},
			{
				'id': 2,
				'text': 'World'
			}
		])
	
	
		
 
if __name__ == '__main__':
	unittest.main() 

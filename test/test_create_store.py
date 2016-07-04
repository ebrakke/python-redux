import unittest

from python_redux import create_store, combine_reducers
from helpers.action_creators import add_todo, dispatch_in_middle, throw_error, unknown_action
from helpers.reducers import reducers

class TestCreateStoreMethod(unittest.TestCase):
  def test_exposes_public_API(self):
    store = create_store(combine_reducers(reducers))
    methods = store.keys()
    
    self.assertEqual(len(methods), 4)
    self.assertTrue('subscribe' in methods)
    self.assertTrue('dispatch' in methods)
    self.assertTrue('get_state' in methods)
    self.assertTrue('replace_reducer' in methods)
 
if __name__ == '__main__':
  unittest.main() 

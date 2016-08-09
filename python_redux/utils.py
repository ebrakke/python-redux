from .exceptions import (
	UndefinedStateReturned, UndefinedStateFromRandomType)

ACTION_TYPES = {
	'INIT': '@@redux/INIT'
}

def is_function(func):
	if hasattr(func, '__call__'):
		return True
	return False
	
def assert_reducer_sanity(reducers):
	for key in reducers.keys():
		reducer = reducers[key]
		initial_state = reducer(None, { 'type': ACTION_TYPES['INIT'] })

		if initial_state is None:
			raise UndefinedStateReturned('Reducer "{}" returned undefined during initialization. If the state passed to the reducer is undefined, you must explicitly return the initial state. The initial state may not be undefined.'.format(key))
		ty = '@@redux/PROBE_UNKNOWN_ACTION_{}'.format('.'.join(choice('0123456789ABCDEFGHIJKLM') for i in range(20)))
		if reducer(None, { 'type': ty }) is None:
			msg = 'Reducer "{}" returned undefined when probed with a random type. Don\'t try to handle {} or other actions in "redux/*" \n namespace. They are considered private. Instead, you must return the current state for any unknown actions, unless it is undefined, in which case you must return initial state, regardless of the action type. The initial state may not be undefined.'.format(key, ACTION_TYPES['INIT'])
			raise UndefinedStateFromRandomType(msg)

def get_undefined_state_error_message(key, action):
	action_type = action and action['type']
	action_name = action_type and str(action_type) or 'an action'
	return 'Given action "{}", reducer "{}" returned None.  To ignore an action you must return the previous state'.format(action_name, key)

def get_unexpected_state_shape_warning_message(input_state, reducers, action, unexpected_key_cache):
	reducer_keys = reducers.keys()
	argument_name = 'preloaded_state argument passed to create_store' if action and type(action) == dict and action.get('type') == ACTION_TYPES['INIT'] else 'previous state recieved by reducer'
	
	if len(reducer_keys) == 0:
		return 'Store does not have a valid reducer. Make sure the argument passed to combine_reducers is an object whose values are reducers.'
	
	if not type(input_state) == dict:
		return 'The {} has an unexpected type of {}. Expected argument to be an object with the following keys: "{}"'.format(
			argument_name,
			str(type(input_state)).replace('\'', '"'),
			'", "'.join(reducer_keys)
		)
	
	unexpected_keys = [key for key in input_state.keys() if not reducers.get(key) and not unexpected_key_cache.get(key)]
	for key in unexpected_keys:
		unexpected_key_cache[key] = True
	
	if len(unexpected_keys) > 0:
		return 'Unexpected {} "{}" found in {}. Expected to find one of the known reducer keys instead: "{}". Unexpected keys will be ignored.'.format(
			'keys' if len(unexpected_keys) > 1 else 'key',
			'", "'.join(unexpected_keys),
			argument_name,
			'", "'.join(reducer_keys)
		)
		
def compose(*funcs):
	"""Composes single-argument functions from right to left
	:param funcs: The functions to compose from left to right
	:return: The composed functions from right to left
	:rtype: Function
	
	Usage::
		>>> compose(f, g, h) # same as lambda *x: f(g(h(*x)))
	"""
	if len(funcs) == 0:
		return lambda *args: args[0] if args else None
	if len(funcs) == 1:
		return funcs[0]
	
	# reverse array so we can reduce from left to right
	funcs = list(reversed(funcs))
	last = funcs[0]
	rest = funcs[1:]
	
	def composition(*args):
		composed = last(*args)
		for f in rest:
			composed = f(composed)
		return composed
	return composition
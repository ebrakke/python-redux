from utils.warning import warning
from random import choice

ACTION_TYPES = {
	'INIT': '@@redux/INIT'
}

def get_undefined_state_error_message(key, action):
	action_type = action and action['type']
	action_name = action_type and str(action_type) or 'an action'
	
	return 'Given action {}, reducer {} returned None.  To ignore an action you must return the previous state'

def get_unexpected_state_shape_warning_message(input_state, reducers, action, unexpected_key_cache):
	reducer_keys = reducers.keys()
	argument_name = 'preloaded_state argument passed to create_store' if action and action.get('type') == ACTION_TYPES['INIT'] else 'previous state recieved by reducer'
	
	if len(reducer_keys) == 0:
		return 'Store does not have a valid reducer. Make sure the argument passed to combine_reducers is an object whose values are reducers.'
	
	if not type(input_state) == dict:
		return 'The {} has unexpected type of {}. Expected argument to be an object with the following keys: {}'.format(
			argument_name,
			type(input_state),
			', '.join(reducer_keys)
		)
	
	unexpected_keys = [k for k in input_state.keys() if not reducers.get(key) and not unexpected_key_cache[key]]
	for key in unexpected_keys:
		unexpected_key_cache[key] = true
	
	if len(unexpected_keys) > 0:
		'Unexpected {} "{}" found in {}. Expected to find one of the known reducer keys instead: "{}". Unexpected keys will be ignored.'.format(
			'keys' if len(unexpected_keys) > 1 else 'key',
			'", "'.join(unexpected_keys),
			argument_name,
			'", "'.join(reducer_keys)
		)
	
def assert_reducer_sanity(reducers):
	for key in reducers.keys():
		reducer = reducers[key]
		initial_state = reducer(None, { 'type': ACTION_TYPES['INIT'] })
		
		if initial_state is None:
			raise Exception('Reducer "{}" returned undefined during initialization. If the state passed to the reducer is undefined, you must explicitly return the initial state. The initial state may not be undefined.'.format(key))
		type = '@@redux/PROBE_UNKNOWN_ACTION_{}'.format('.'.join(choice('0123456789ABCDEFGHIJKLM') for i in range(20)))
		if reducer(None, { 'type': type }) is None:
			raise Exception("""
			Reducer "{}" returned undefined when probed with a random type.
			Don't try to handle ${ActionTypes.INIT} or other actions in "redux/*"
			namespace. They are considered private. Instead, you must return the
			current state for any unknown actions, unless it is undefined, 
			in which case you must return the initial state, regardless of the
			action type. The initial state may not be undefined.`
			""".format(key))
	
"""
 * Turns an object whose values are different reducer functions, into a single
 * reducer function. It will call every child reducer, and gather their results
 * into a single state object, whose keys correspond to the keys of the passed
 * reducer functions.
 *
 * @param {Object} reducers An object whose values correspond to different
 * reducer functions that need to be combined into one. One handy way to obtain
 * it is to use ES6 `import * as reducers` syntax. The reducers may never return
 * undefined for any action. Instead, they should return their initial state
 * if the state passed to them was undefined, and the current state for any
 * unrecognized action.
 *
 * @returns {Function} A reducer function that invokes every reducer inside the
 * passed object, and builds a state object with the same shape.
"""
def combine_reducers(reducers):
	reducer_keys = reducers.keys()
	final_reducers = {}
	for key in reducer_keys:
		if hasattr(reducers[key], '__call__'):
			final_reducers[key] = reducers[key]
	
	final_reducer_keys = final_reducers.keys()
	sanity_error = [None]
	unexpected_key_cache = {}
	
	try:
		assert_reducer_sanity(final_reducers)
	except Exception as e:
		sanity_error[0] = e
	
	def combination(state=None, action = None):
		if state is None:
			state = {}
		if (sanity_error[0]):
			raise sanity_error[0]
		warning_message = get_unexpected_state_shape_warning_message(state, final_reducers, action, unexpected_key_cache)
		if warning_message:
			warning(warning_message)
		
		has_changed = False
		next_state = {}
		for key in final_reducer_keys:
			reducer = final_reducers.get(key)
			previous_state_for_key = state.get(key)
			next_state_for_key = reducer(previous_state_for_key, action)
			if next_state_for_key is None:
				error_message = get_undefined_state_error_message(key, action)
				raise Exception(error_message)
			next_state[key] = next_state_for_key
			has_changed = has_changed or next_state_for_key != previous_state_for_key
		return next_state if has_changed else state
	return combination
	
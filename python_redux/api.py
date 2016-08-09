import warnings
from copy import deepcopy
from .utils import (
	is_function, ACTION_TYPES, get_undefined_state_error_message,
	get_unexpected_state_shape_warning_message, compose)
from .exceptions import (
	BindActionCreatorException, UndefinedStateFromRandomType, UndefinedStateReturned)
from .models import Store, MiddlewareAPI

def apply_middleware(*middlewares):
	"""Creates a store enhancer that applies middleware to the dispatch method of the Redux store.
	:param middlewares: The middleware chain to be applied
	:return: A store enhancer applying the middlewares
	:rtype: Function
	"""
	def chain(create_store):
		def inner(reducer, **kwargs):	
			store = create_store(reducer, **kwargs)
			dispatch = store.dispatch
			chain = []
			
			middleware_api = MiddlewareAPI(store.get_state, lambda action: dispatch(action))
			chain = [middleware(middleware_api) for middleware in middlewares]
			dispatch = compose(*chain)(store.dispatch)
			
			store_to_return = deepcopy(store)
			store_to_return.dispatch = dispatch
			return store_to_return
		return inner
	return chain
	
def bind_action_creator(action_creator, dispatch):
	""" Wraps an action creator with the dispatch callable
	:param action_creator: A function which is an action creator
	:dispatch: the dispatch function for the redux store
	:return: Action creator wrapped in the dispatch callable
	:rtype: Function
	"""
	return lambda *args: dispatch(action_creator(*args))
	
def bind_action_creators(action_creators, dispatch):
	"""Turns an object whose values are action creators, into an object with the
 	same keys, but with every function wrapped into a `dispatch` call so they
 	may be invoked directly. 
	:param action_creators: a single action creator or an object with action creators
	:param dispatch: The dispatch function for the redux store
	:return: object with action creators wrapped in dispatch call
 	:rtype: Function or Dictionary
	"""
	
	if is_function(action_creators):
		return bind_action_creator(action_creators, dispatch)
	if type(action_creators) != dict:
		raise BindActionCreatorException('bind_action_creators expected an object or a function, instead received {}.'.format(type(action_creators)))
	
	bound_action_creators = {}
	for key in action_creators:
		action_creator = action_creators[key]
		if is_function(action_creator):
			bound_action_creators[key] = bind_action_creator(action_creator, dispatch)
	return bound_action_creators
	
def combine_reducers(reducers):
	""" Turns an object of different recuers into a single reducer function
	:param reducers: A dictionary of reducer functions to represent the state
	:return: A function which acts as a single reducer for the state tree
	:rtype: Function
	"""
	reducer_keys = reducers.keys()
	final_reducers = {key: reducers[key] for key in reducer_keys if is_function(reducers[key])}
	
	final_reducer_keys = final_reducers.keys()
	sanity_error = None
	unexpected_key_cache = {}
	
	try:
		assert_reducer_sanity(final_reducers)
	except (UndefinedStateFromRandomType, UndefinedStateReturned) as e:
		sanity_error = e
	
	def combination(state=None, action = None):
		if state is None:
			state = {}
		if sanity_error:
			raise sanity_error
		warning_message = get_unexpected_state_shape_warning_message(state, final_reducers, action, unexpected_key_cache)
		if warning_message:
			warnings.warn(warning_message)
		
		has_changed = False
		next_state = {}
		for key in final_reducer_keys:
			reducer = final_reducers.get(key)
			previous_state_for_key = state.get(key) if type(state) == dict else state
			next_state_for_key = reducer(previous_state_for_key, action)
			if next_state_for_key is None:
				error_message = get_undefined_state_error_message(key, action)
				raise UndefinedStateReturned(error_message)
			next_state[key] = next_state_for_key
			has_changed = has_changed or next_state_for_key != previous_state_for_key
		return next_state if has_changed else state
	return combination
	
def create_store(reducer, **kwargs):
	preloaded_state = kwargs.get('preloaded_state')
	enhancer = kwargs.get('enhancer')
	if enhancer is not None:
		if not is_function(enhancer):
			raise TypeError('Expected the enhancer to be a function')
		return enhancer(create_store)(reducer, preloaded_state=preloaded_state)
	
	return Store(reducer, **kwargs)


from .utils import (
	is_function, ACTION_TYPES)

from .exceptions import DispatchInMiddle

class Store:
	"""A Redux Store. Creates a Redux store that holds the state tree.
	:param self:
	:param reducer: A function that returns the next state tree, given the current state tree and the action to handle.
	:param preloaded_state: (optional) Dictionary of the initial state tree
	"""
	def __init__(self, reducer, **kwargs):
		preloaded_state = kwargs.get('preloaded_state')
		
		if not is_function(reducer):
			raise TypeError('Expected the reducer to be a function')
		
		self._current_reducer = reducer
		self._current_state = preloaded_state
		self._current_listeners = []
		self._next_listeners = self._current_listeners
		self._is_dispatching = False
		
		self.dispatch({ 'type': ACTION_TYPES['INIT']})
	
	def ensure_can_mutate_next_listeners(self):
		if self._next_listeners == self._current_listeners:
			self._next_listeners = [c for c in self._current_listeners]
	
	@property
	def state(self):
		"""Reads the state tree managed by the store.
		:return: the current state
		"""
		return self._current_state
	
	#TODO: Should this be removed in favor of property?
	def get_state(self):
		"""Reads the state tree managed by the store.
		:return: the current state
		"""
		return self._current_state
	
	def subscribe(self, listener):
		"""Adds a change listener. It will be called any time an action is dispatched.
		:param listener: A callback to be invoked on every dispatch
		:return: A function to unsubscribe from the dispatch events
		:rtype: Function
		"""
		if not hasattr(listener, '__call__'):
			raise Exception('Expected listener to be a function')
		
		is_subscribed = True
		self.ensure_can_mutate_next_listeners()
		self._next_listeners.append(listener)
		
		def unsubscribe():
			nonlocal is_subscribed
			if not is_subscribed:
				return
			is_subscribed = False
			self.ensure_can_mutate_next_listeners()
			index = self._next_listeners.index(listener)
			del self._next_listeners[index]
		
		return unsubscribe
	
	def dispatch(self, action):
		"""Dispatches an action. It is the only way to trigger a state change.
		:param action: Dictionary representing what has changed
		:return: the action
		:rtype: Dictionary
		"""
		if not type(action) == dict:
			raise TypeError('Actions must be plain dictionaries.  Consider adding middleware to change this')
		if action.get('type') is None:
			raise TypeError('Actions may not have an undefined "type" property.\n Have you misspelled a constant?')
		if self._is_dispatching:
			raise DispatchInMiddle('Reducers may not dispatch actions')
		
		try:
			self._is_dispatching = True
			self._current_state = self._current_reducer(self._current_state, action)
		finally:
			self._is_dispatching = False
		
		listeners = self._current_listeners = self._next_listeners
		for l in listeners:
			l()
		return action	
		
	def replace_reducer(self, next_reducer):
		if not hasattr(next_reducer, '__call__'):
			raise TypeError('Expected next_reducer to be a function')
		self._current_reducer = next_reducer
		self.dispatch({ 'type': ACTION_TYPES['INIT'] })
		

class MiddlewareAPI:
	def __init__(self, get_state, dispatch):
		self.get_state = get_state
		self.dispatch = dispatch
		
	
ACTION_TYPES = {
	'INIT': '@@redux/INIT'
}
class Store:
	def __init__(self, reducer, **kwargs):
		"""Initializer for a Redux Store. Creates a Redux store that holds the state tree.
		:param self:
		:param reducer: A function that returns the next state tree, given the current state tree and the action to handle.
		:param preloaded_state: (optional) Dictionary of the initial state tree
		:param enhancer: (optional) A function to enhance the store (e.g. apply_middleware)
		Usage::
		>>> from python_redux import Store
		>>> store = Store(reducer)
		"""
		enhancer = kwargs.get('enhancer')
		preloaded_state = kwargs.get('preloaded_state')
		
		if enhancer is not None :
			if not hasattr(enhancer, '__call__'):
				raise Exception('Expected the enhancer to be a function')
			# TODO: implement enhancers
		if not hasattr(reducer, '__call__'):
			raise Exception('Expected the reducer to be a function')
		
		self._current_reducer = reducer
		self._current_state = preloaded_state
		self._current_listeners = []
		self._next_listeners = self._current_listeners
		self._is_dispatching = False
	
	def ensure_can_mutate_next_listeners(self):
		if self._next_listeners == self._current_listeners:
			self._next_listeners = [c for c in self._current_listeners]
	
	def get_state(self):
		"""Reads the state tree managed by the store.
		:return: the current state
		:rtype: Dictionary
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
			self._next_listeners = [l for l in self._next_listeners if l != listener]
		
		return unsubscribe
	
	def dispatch(self, action):
		"""Dispatches an action. It is the only way to trigger a state change.
		:param action: Dictionary representing what has changed
		:return: the action
		:rtype: Dictionary
		"""
		if not type(action) == dict:
			raise Exception('Actions must be plain dictionaries.  Consider adding middleware to change this')
		if action.get('type') is None:
			raise Exception('Actions may not have an undefined "type" property.\n Have you misspelled a constant?')
		if self._is_dispatching:
			raise Exception('Reducers may not dispatch actions')
		
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
			raise Exception('Expected next_reducer to be a function')
		self._current_reducer = next_reducer
		self.dispatch({ 'type': ACTION_TYPES['INIT'] })
	
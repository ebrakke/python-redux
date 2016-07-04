from compose import compose
"""
 * Creates a store enhancer that applies middleware to the dispatch method
 * of the Redux store. This is handy for a variety of tasks, such as expressing
 * asynchronous actions in a concise manner, or logging every action payload.
 *
 * See `redux-thunk` package as an example of the Redux middleware.
 *
 * Because middleware is potentially asynchronous, this should be the first
 * store enhancer in the composition chain.
 *
 * Note that each middleware will be given the `dispatch` and `getState` functions
 * as named arguments.
 *
 * @param {*Function} middlewares The middleware chain to be applied.
 * @returns {Function} A store enhancer applying the middleware.
"""
def apply_middleware(*middlewares):
	def chain(create_store):
		def inner(reducer, preloaded_state, enhancer):
			store = create_store(reducer, preloaded_state, enhancer)
			dispatch = store.get('dispatch')
			chain = []
			
			middleware_api = {
				get_state: store.get('get_state'),
				dispatch: lambda action: dispatch(action)
			}
			chain = map(lambda middleware: middleware(middleware_api), middlewares)
			dispatch = compose(*chain)(store.get('dispatch'))
			
			store_to_return = store.copy()
			store_to_return['dispatch'] = dispatch
			return store_to_return
	return chain
 
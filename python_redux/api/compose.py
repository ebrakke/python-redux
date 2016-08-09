"""
 * Composes single-argument functions from right to left. The rightmost
 * function can take multiple arguments as it provides the signature for
 * the resulting composite function.
 *
 * @param {...Function} funcs The functions to compose.
 * @returns {Function} A function obtained by composing the argument functions
 * from right to left. For example, compose(f, g, h) is identical to doing
 * lambda *args: f(g(h(*args)))
"""
def compose(*funcs):
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


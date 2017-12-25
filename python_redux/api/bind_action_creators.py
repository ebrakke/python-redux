def bind_action_creator(action_creator, dispatch):
    return lambda *args: dispatch(action_creator(*args))


def bind_action_creators(action_creators=None, dispatch=None):
    """
    Turns an object whose values are action creators, into an object with the
    same keys, but with every function wrapped into a `dispatch` call so they
    may be invoked directly. This is just a convenience method, as you can call
    `store['dispatch'](MyActionCreators['doSomething']())` yourself just fine.

    For convenience, you can also pass a single function as the first argument,
    and get a function in return.

    @param {Function|Object} actionCreators An object whose values are action
    creator functions.
    You may also pass a single function.

    @param {Function} dispatch The `dispatch` function available on your Redux
    store.

    @returns {Function|Object} The object mimicking the original object, but with
    every action creator wrapped into the `dispatch` call. If you passed a
    function as `actionCreators`, the return value will also be a single
    function.
    """
    if hasattr(action_creators, '__call__'):
        return bind_action_creator(action_creators, dispatch)
    if type(action_creators) != dict or action_creators == None:
        raise Exception('bind_action_creators expected an object or a function, instead received {}.'.format(
            'None' if action_creators == None else type(action_creators)))

    bound_action_creators = {}
    for key in action_creators:
        action_creator = action_creators[key]
        if hasattr(action_creator, '__call__'):
            bound_action_creators[key] = bind_action_creator(
                action_creator, dispatch)
    return bound_action_creators

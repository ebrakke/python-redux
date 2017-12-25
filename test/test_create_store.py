import unittest
import unittest.mock as mock

from python_redux import create_store, Store
from test.helpers.reducers import reducers


class TestCreateStoreMethod(unittest.TestCase):
    def test_accepts_and_applies_enhancer(self):
        empty_array = []

        def spy_enhancer(reducer, **kwargs):
            self.assertEqual(reducer, reducers['todos'])
            self.assertEqual(kwargs.get('preloaded_state'), empty_array)
            vanilla_store = Store(reducer, **kwargs)
            vanilla_store.dispatch = mock.MagicMock(
                side_effect=vanilla_store.dispatch)
            return vanilla_store
        return spy_enhancer

        store = create_store(
            reducers['todos'], preloaded_state=empty_array, enhancer=spy_enhancer)
        action = add_todo('Hello')
        store.dispatch(action)
        self.assertEqual(store.dispatch.call_args_list, [mock.call(action)])
        self.assertEqual(store.state, [{
            'id': 1,
            'text': 'Hello'
        }])

    def test_throws_if_enhancer_is_neither_undefined_or_a_function(self):
        with self.assertRaises(Exception):
            create_store(reducers['todos'], enhancer={})
        with self.assertRaises(Exception):
            create_store(reducers['todos'], enhancer=[])
        with self.assertRaises(Exception):
            create_store(reducers['todos'], enhancer=False)
        try:
            create_store(reducers['todos'], enhancer=None)

            create_store(reducers['todos'], enhancer=lambda x: x)

            create_store(reducers['todos'])
            create_store(reducers['todos'], preloaded_state=[])
            create_store(reducers['todos'], preloaded_state={})
        except Exception:
            self.fail('Should not have thrown an exception')


if __name__ == '__main__':
    unittest.main()

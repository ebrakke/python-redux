class BindActionCreatorException(TypeError):
  """The action creator was not a Dictionary or Function"""

class UndefinedStateReturned(Exception):
  """The reducer did not return a state"""

class UndefinedStateFromRandomType(Exception):
  """The reducer tried to handle an action it should not have"""

class DispatchInMiddle(Exception):
  """The reducer tried to dipatch an action in the middle of dispatching"""
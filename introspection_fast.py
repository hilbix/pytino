# Python introspection to some standard libraries and more
# Warning, this is somewhat slow at init time, but later very fast

import introspection_impl
from clo import moduledictgetter

introspection_impl._impl(__name__, lambda m,p,w: moduledictgetter(m, p, w))

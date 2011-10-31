# Python introspection to some standard libraries and more
# Warning, this is somewhat slow at init time, but later very fast
#
# run this like
# python -m pytino/introspection/fast

from pytino import clo
from pytino import introspection

introspection._impl(lambda m,p,w: clo.moduledictgetter(m, p, w))

if __name__ == '__main__':
        print introspection.sockAF(1)

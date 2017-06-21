#!/usr/bin/env python3
#
# depgraph - Analyze and graph Java project dependencies
# Copyright (C) 2017 Sebastian Götte
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import sqlite3
import textwrap
from collections import Counter

_GRAPH_TEMPLATE = '''
digraph G {{
    graph [sep=0.5];

    subgraph interface {{
{interfaces}
    }}

    subgraph class {{
        node [shape=box];
{classes}
    }}

    subgraph abstract_class {{
        node [shape=box, style=bold];
{abstract_classes}
    }}

    subgraph enum {{
        node [style=dotted];
{enums}
    }}

    subgraph extends {{
        edge [weight=2.0];
        edge [style=bold];
{extends}
    }}
    
    subgraph interface_extends {{
        edge [len=1.0, weight=5.0];
{iextends}
    }}

    subgraph implements {{
        edge [len=1.0, weight=1.0];
{implements}
    }}

    subgraph references {{
        edge [color=gray, weight=0];
/* {references} */
    }}
}}
'''

def db_to_dot(conn):
    cur = conn.cursor()
    escape = lambda s: '"{}"'.format(s.replace('org.bbaw.bts.', '*'))

    fetch_type = lambda t: { e for e, in cur.execute('SELECT types.fullname FROM types INNER JOIN metatypes ON types.type = metatypes.id WHERE metatypes.name = ?', (t,)) }
    fetch_relation = lambda table: set(cur.execute('SELECT srctype.fullname, tgttype.fullname FROM {0} INNER JOIN types AS srctype ON {0}.source = srctype.id INNER JOIN types AS tgttype ON {0}.target = tgttype.id'.format(table)))

    interfaces = fetch_type('interface')
    classes = fetch_type('class')
    abstract_classes = fetch_type('abstract_class')
    enums = fetch_type('enum')

    extends = fetch_relation('extends')
    implements = fetch_relation('implements')
    iextends = { (a, b) for a, b in implements if a in interfaces and b in interfaces }
    implements -= iextends
    references = fetch_relation('reference')

    all_types = interfaces | classes | abstract_classes | enums
    inheritance = extends | implements
    inheritance_any = Counter( e for edge in inheritance for e in edge )
    exclude_types = { t for t in all_types if inheritance_any[t] == 0 } # exclude single nodes or two-subgraphs

    format_type = lambda elems: textwrap.indent('\n'.join( '{};'.format(escape(e)) for e in elems-exclude_types ), ' '*8)
    format_relation = lambda elems: textwrap.indent('\n'.join( '{} -> {};'.format(escape(a), escape(b)) for a, b in elems if not a in exclude_types or b in exclude_types ), ' '*8)

    return _GRAPH_TEMPLATE.format(
            classes=format_type(classes),
            interfaces=format_type(interfaces),
            abstract_classes=format_type(abstract_classes),
            enums=format_type(enums),
            extends=format_relation(extends),
            implements=format_relation(implements),
            iextends=format_relation(iextends),
            references=format_relation(references))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('db', help='The sqlite3 relationship database file to read')
    parser.add_argument('output', help='The DOT output file to write')
    args = parser.parse_args()
    
    db = sqlite3.connect(args.db)
    with open(args.output, 'w') as f:
        with db as conn:
            f.write(db_to_dot(conn))


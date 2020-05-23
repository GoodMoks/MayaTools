import maya.cmds as cmds

def break_con(obj=None, attr=None):
    """ Breaks input connections

    :param obj: 'list' list of objects
    :param attr: 'list' attr to disconnect
    """
    if not obj:
        obj = cmds.ls(sl=True, fl=True)

    if isinstance(obj, basestring):
        obj = [obj]

    if obj:
        for o in obj:
            con_pairs = []
            try:
                con = cmds.listConnections(o, plugs=True, connections=True, destination=False)
                if con:
                    con_pairs.extend(zip(con[1::2], con[::2]))

                for source, dest in con_pairs:
                    if attr:
                        full_Attr = o + attr
                        if dest == full_Attr:
                            cmds.disconnectAttr(source, dest)
                    else:
                        cmds.disconnectAttr(source, dest)
            except:
                pass


def connect_nodes(obj=None,
                  node_type=None, plugs=False,
                  sourse=True, dest=True):

    """ Return connection nodes
    :param obj: 'str' object to check
    :param node_type: 'str' type of nodes
    :param plugs: 'bool' return with connect attribute or not
    :param sourse: 'bool' return input nodes
    :param dest: 'bool' return output nodes
    :return: 'dict' nodes{'input':[...], 'output':[...]}
    """

    if obj and sourse or dest:
        return_dict = dict(
            input=None,
            output=None
        )
        nodes_dict = dict(
            input=cmds.listConnections(obj, plugs=plugs, source=sourse, destination=False),
            output=cmds.listConnections(obj, plugs=plugs, source=False, destination=dest)
        )
        for key, nodes in nodes_dict.iteritems():
            key_filter = []
            if nodes:
                for node in nodes:
                    if node_type:
                        node = [x for x in [node] if cmds.objectType(node) == node_type if x]
                    key_filter.append(node)

            if key_filter:
                return_dict[key] = key_filter
            if not key_filter:
                return_dict.pop(key)

        print return_dict








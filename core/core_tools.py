from attribute import *
from connections import *
from constraint import *
from dag import *
from utils import *
from transform import *
from vector import *
from base import *

if __name__ == '__main__':
    # all methods

    ''' utils '''
    create_goal()

    ''' transform '''
    align_transform()

    ''' attribute '''
    add_attr()

    ''' base '''
    get_MObject()
    get_history()
    isShape()
    get_instances()

    ''' connections '''
    get_common_connections()
    disconnect_objects()
    get_connections_cb()

    ''' constraint '''
    is_constraint()
    get_connected_constraint()
    get_target_constraint()
    restore_constraint()
    duplicate_constraint_connections()

    ''' dag '''
    get_children()
    get_parent()

    ''' vector '''
    get_distance()
    getDistance()

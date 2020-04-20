import MayaTools.tools.joint_chain_breaker.joint_chain_breacker as joint_chain_breacker

reload(joint_chain_breacker)


def joint_insert(dp, pf):
    if joint_chain_breacker.list_of_jnt():

        par, ch = joint_chain_breacker.list_of_jnt()

        v1 = joint_chain_breacker.get_transform(par)
        v2 = joint_chain_breacker.get_transform(ch)

        distance = v1 - v2
        div_dist = joint_chain_breacker.vector_divide(distance, dp)

        added_jnt = joint_chain_breacker.insert_jnt(v2, div_dist, dp, par)

        if pf:
            joint_chain_breacker.parent_jnt(par, added_jnt, ch)

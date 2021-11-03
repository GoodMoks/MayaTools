from maya import cmds


def chunk_decorator(func):
    def function(*args, **kwargs):
        cmds.undoInfo(openChunk=True)
        func(*args, **kwargs)
        cmds.undoInfo(closeChunk=True)

    return function


class Test:
    def __init__(self):
        self.create_cube()
        pass

    @chunk_decorator
    def create_cube(self):
        for i in range(2):
            cube = cmds.polyCube()[0]
            cmds.setAttr('{}.ty'.format(cube), i + 10)


@chunk_decorator
def simple():
    for i in range(2):
        print(i)
        cube = cmds.polyCube()[0]
        cmds.setAttr('{}.ty'.format(cube), i + 10)

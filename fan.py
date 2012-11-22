import bpy
import bmesh

class MoveFacesAlongNormalsOperator(bpy.types.Operator):
    '''Tooltip'''
    bl_idname = "object.move_faces_along_normals_operator"
    bl_label = "Move Faces Along Normals"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.object.mode == 'EDIT'

    def execute(self, context):
        factor = 1
        bm = bmesh.from_edit_mesh(context.object.data)
        for face in bm.faces:
            if face.select:
                normal = face.normal
                for vertex in face.verts:
                    vertex.co.x += normal.x * factor
                    vertex.co.y += normal.y * factor
                    vertex.co.z += normal.z * factor
        return {'FINISHED'}

def register():
    bpy.utils.register_class(MoveFacesAlongNormalsOperator)

def unregister():
    bpy.utils.unregister_class(MoveFacesAlongNormalsOperator)

if __name__ == "__main__":
    register()

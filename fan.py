import bpy
import bmesh

# Operator to move the faces
class MoveFacesAlongNormalsOperator(bpy.types.Operator):
    '''Move the faces along individual normal vectors.'''
    bl_idname = "fan.move_faces_along_normals_operator"
    bl_label = "Move Faces Along Normals"
    bl_options = {'REGISTER', 'UNDO'}
    
    distance = bpy.props.FloatProperty(name="Distance")

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.object.mode == 'EDIT'

    def execute(self, context):
        bm = bmesh.from_edit_mesh(context.object.data)
        for face in bm.faces:
            if face.select:
                normal = face.normal
                for vertex in face.verts:
                    vertex.co.x += normal.x * self.distance
                    vertex.co.y += normal.y * self.distance
                    vertex.co.z += normal.z * self.distance
        context.area.tag_redraw()
        return {'FINISHED'}

# Draw the operator in the menu
def menu_draw(self, context):
    self.layout.operator("fan.move_faces_along_normals_operator")

def register():
    bpy.types.VIEW3D_MT_edit_mesh_specials.append(menu_draw)
    bpy.utils.register_class(MoveFacesAlongNormalsOperator)

def unregister():
    bpy.types.VIEW3D_MT_edit_mesh_specials.remove(menu_draw)
    bpy.utils.unregister_class(MoveFacesAlongNormalsOperator)

if __name__ == "__main__":
    register()

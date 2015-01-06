import bpy
import bmesh
import mathutils
import math

bl_info = {
    "name": "Faces Along Normals",
    "description": "Move faces along individual normals.",
    "author": "Márcio Daniel da Rosa",
    "version": (1, 1),
    "blender": (2, 73, 0),
    "location": "3D View (Edit Mode) > Specials menu (W key) > Move Faces Along Normals",
    "warning": "",
    "category": "Mesh"}

# Operator to move the faces. It first calculates a new position for each vertex of the face, for all
# selected faces. So, if a vertex is shared with more than one selected face, it will have more than
# one calculated position. So, the final position is calculated given a list of calculated positions
# for that vertex.
class MoveFacesAlongNormalsOperator(bpy.types.Operator):
    '''Move the faces along individual normal vectors.'''
    bl_idname = "fan.move_faces_along_normals_operator"
    bl_label = "Move Faces Along Normals"
    bl_options = {'REGISTER', 'UNDO'}
    
    distance = bpy.props.FloatProperty(name="Distance", subtype='DISTANCE', step=1, precision=3)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.object.mode == 'EDIT'

    # Executes the translation for each selected face. If no faces are affected, then translate all faces.
    def execute(self, context):
        if self.distance != 0:
            bm = bmesh.from_edit_mesh(context.object.data)
            self.translate_faces_or_edges_or_verts(bm)
            bm.normal_update()
            context.area.tag_redraw()
        return {'FINISHED'}

    # Move the faces, edges or vertices (given the selection mode). Input: the bmesh and a flag to define if only
    # the selected faces must be translated, or all faces must be translated.
    def translate_faces_or_edges_or_verts(self, mesh):
        calculated_translations_by_vertex_index = dict()
        #if 'VERT' in mesh.select_mode:
        if 'EDGE' in mesh.select_mode:
            self.calculate_translation_for_mesh_edges(calculated_translations_by_vertex_index, mesh)
        elif 'FACE' in mesh.select_mode:
            self.calculate_translation_for_mesh_faces(calculated_translations_by_vertex_index, mesh)
        self.translate_verts(calculated_translations_by_vertex_index, mesh)

    def calculate_translation_for_mesh_edges(self, results_dict, mesh):
        for edge in mesh.edges:
            if edge.select:
                self.calculate_translations_for_edge_verts(results_dict, edge)

    def calculate_translation_for_mesh_faces(self, results_dict, mesh):
        for face in mesh.faces:
            if face.select:
                self.calculate_translations_for_face_verts(results_dict, face)
    
    # Calculate the translation for each vertex in the face, along the face normal. Input: the dict where
    # the translation vector will be stored by the vertex index and the face.
    def calculate_translations_for_face_verts(self, results_dict, face):
        for vertex in face.verts:
            self.add_translation_vector_to_vertex(results_dict, face.normal, vertex)

    def calculate_translations_for_edge_verts(self, results_dict, edge):
        for vertex in edge.verts:
            for face in edge.link_faces:
                self.add_translation_vector_to_vertex(results_dict, face.normal, vertex)

    def add_translation_vector_to_vertex(self, results_dict, vector, vertex):
        translation = mathutils.Vector()
        translation.x = vector.x * self.distance
        translation.y = vector.y * self.distance
        translation.z = vector.z * self.distance
        if vertex.index in results_dict:
            results_dict[vertex.index].append(translation)
        else:
            results_dict[vertex.index] = [translation]

    # Calculates the position for each vertex and updates the coordinates. Input: the bmesh and the dictionary
    # with the calculated translations for the vertices.
    def translate_verts(self, translations_by_vertex_index, mesh):
        mesh.verts.ensure_lookup_table()
        for vertex_index in translations_by_vertex_index.keys():
            vertex = mesh.verts[vertex_index]
            translations = translations_by_vertex_index[vertex_index]
            sum = self.sum_points(translations)
            cathetus = self.distance
            angle = sum.angle(translations[0])
            h = cathetus / math.cos(angle)
            sum.length = abs(h)
            vertex.co += sum
    
    # input: list of coordinates, output: a coordinate, the sum of the input coordinates
    def sum_points(self, coordinates):
        final_coordinate = mathutils.Vector((0, 0, 0))
        for co in coordinates:
            final_coordinate += co
        return final_coordinate
    
# Draws the operator in the specials menu
def specials_menu_draw(self, context):
    self.layout.operator("fan.move_faces_along_normals_operator")

# Draws the operator in the faces menu
def faces_menu_draw(self, context):
    self.layout.separator()
    self.layout.operator("fan.move_faces_along_normals_operator")

def register():
    bpy.utils.register_class(MoveFacesAlongNormalsOperator)
    bpy.types.VIEW3D_MT_edit_mesh_specials.append(specials_menu_draw)
    bpy.types.VIEW3D_MT_edit_mesh_faces.append(faces_menu_draw)

def unregister():
    bpy.utils.unregister_class(MoveFacesAlongNormalsOperator)
    bpy.types.VIEW3D_MT_edit_mesh_specials.remove(specials_menu_draw)
    bpy.types.VIEW3D_MT_edit_mesh_faces.remove(faces_menu_draw)
    
if __name__ == "__main__":
    register()
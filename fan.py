import bpy
import bmesh
import mathutils
import math

bl_info = {
    "name": "Move Along Normals",
    "description": "Move vertices, edges or faces along individual normals.",
    "author": "Márcio Daniel da Rosa",
    "version": (1, 3),
    "blender": (2, 73, 0),
    "location": "3D View (Edit Mode) > Specials menu (W key) > Move Along Normals",
    "warning": "",
    "category": "Mesh"}

# Operator to move the vertices, edges or normals. It first calculates a new position for each selected
# vertex. If a vertex is shared with more than one selected face or edge, it will have more than
# one calculated position. Then, the final position is calculated given a list of calculated positions
# for that vertex.
class MoveFacesAlongNormalsOperator(bpy.types.Operator):
    '''Move the vertices, edges or faces along individual normal vectors.'''
    bl_idname = "fan.move_faces_along_normals_operator"
    bl_label = "Move Along Normals"
    bl_options = {'REGISTER', 'UNDO'}
    
    distance = bpy.props.FloatProperty(name="Distance", subtype='DISTANCE', step=1, precision=3)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.object.mode == 'EDIT'

    def execute(self, context):
        if self.distance != 0:
            mesh = bmesh.from_edit_mesh(context.object.data)
            calculated_translations_by_vertex_index = self.calculate_translations(mesh)
            self.translate_verts(calculated_translations_by_vertex_index, mesh)
            mesh.normal_update()
            context.area.tag_redraw()
        return {'FINISHED'}
        
    # Calculates the translations for each selected vertex. Returns a dictionary with the vectors for each vertex.
    # Input: the bmesh
    def calculate_translations(self, mesh):
        calculated_translations_by_vertex_index = dict()
        self.calculate_translations_for_selected_verts(calculated_translations_by_vertex_index, mesh)
        self.calculate_translations_for_selected_edges(calculated_translations_by_vertex_index, mesh)
        self.calculate_translations_for_selected_faces(calculated_translations_by_vertex_index, mesh)
        return calculated_translations_by_vertex_index

    def calculate_translations_for_selected_verts(self, results_dict, mesh):
        for vertex in mesh.verts:
            if vertex.select and not self.is_vertex_connected_to_a_selected_edge(vertex):
                self.add_translation_vector_to_vertex(results_dict, vertex.normal, vertex)

    def is_vertex_connected_to_a_selected_edge(self, vertex):
        for edge in vertex.link_edges:
            if edge.select:
                return True
        return False

    def calculate_translations_for_selected_edges(self, results_dict, mesh):
        for edge in mesh.edges:
            if edge.select and not self.is_edge_connected_to_a_selected_face(edge):
                self.calculate_translations_for_edge_verts(results_dict, edge)

    def is_edge_connected_to_a_selected_face(self, edge):
        for face in edge.link_faces:
            if face.select:
                return True
        return False

    def calculate_translations_for_selected_faces(self, results_dict, mesh):
        for face in mesh.faces:
            if face.select:
                self.calculate_translations_for_face_verts(results_dict, face)

    def calculate_translations_for_edge_verts(self, results_dict, edge):
        for vertex in edge.verts:
            for face in edge.link_faces:
                self.add_translation_vector_to_vertex(results_dict, face.normal, vertex)
    
    def calculate_translations_for_face_verts(self, results_dict, face):
        for vertex in face.verts:
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

    # Updates the positions of the selected vertices. Input: the dictionary
    # with the calculated translations for the vertices and the bmesh.
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
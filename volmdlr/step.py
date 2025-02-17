#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISO STEP reader/writer.
"""

import time
from typing import List
import numpy as npy

import matplotlib.pyplot as plt
import networkx as nx
import plot_data.graph

import dessia_common.core as dc  # isort: skip
from dessia_common.files import BinaryFile  # isort: skip

import volmdlr
import volmdlr.core
import volmdlr.edges
import volmdlr.faces
import volmdlr.primitives3d
import volmdlr.wires


def set_to_list(step_set):
    """
    Convert a string representation of a set to a list of strings.

    :param step_set: String representation of a set, e.g. "{A,B,C}"
    :type step_set: str
    :return: List of strings, e.g. ["A", "B", "C"]
    :rtype: List[str]
    """
    char_list = step_set.split(',')
    char_list[0] = char_list[0][1:]
    char_list[-1] = char_list[-1][:-1]
    return list(char_list)


def step_split_arguments(function_arg):
    """
    Split the arguments of a function that doesn't start with '(' but end with ')'.

    ex: IN: '#123,#124,#125)'
       OUT: ['#123', '#124', '#125']
    """
    if len(function_arg) > 0 and function_arg[-1] != ')':
        function_arg += ')'
    arguments = []
    argument = ""
    if len(function_arg) > 0 and function_arg[0] == "(":
        function_arg += ")"
    parenthesis = 1
    for char in function_arg:
        if char == "(":
            parenthesis += 1

        if char != "," or parenthesis > 1:
            argument += char
        else:
            arguments.append(argument)
            argument = ""

        if char == ")":
            parenthesis -= 1
            if parenthesis == 0:
                arguments.append(argument[:-1])
                argument = ""
                break
    return arguments


def uncertainty_measure_with_unit(arguments, object_dict):
    """
    Gets the global length uncertainty.

    :param arguments: step primitive arguments
    :param object_dict: dictionary containing already instantiated objects.
    :return: Global length uncertainty.
    """
    length_measure = float(arguments[0].split('(')[1][:-1])
    return length_measure * object_dict[arguments[1]]


def conversion_based_unit_length_unit_named_unit(arguments, object_dict):
    """
    Gets the conversion based unit length.

    :param arguments: step primitive arguments
    :param object_dict: dictionary containing already instantiated objects.
    :return: conversion based unit length.
    """
    return object_dict[arguments[1]]


def length_measure_with_unit(arguments, object_dict):
    """
    Calculates the step file's si unit conversion factor.

    :param arguments: step primitive arguments
    :param object_dict: dictionary containing already instantiated objects.
    :return: si unit conversion factor.
    """
    length_measure = float(arguments[0].split('(')[1][:-1])
    length_si_unit = object_dict[arguments[1]]
    return length_measure * length_si_unit


def length_unit_named_unit_si_unit(arguments, object_dict):
    """
    Gets the length si unit.

    :param arguments: step primitive arguments
    :param object_dict: dictionary containing already instantiated objects.
    :return: length si unit
    """
    si_unit_length = SI_PREFIX[arguments[1]]
    return si_unit_length


def geometric_representation_context_global_uncertainty_assigned_context_global_unit_assigned_context_representation_context(
        arguments, object_dict):
    """
    Gets the global length uncertainty.

    :param arguments: step primitive arguments
    :param object_dict: dictionary containing already instantiated objects.
    :return: Global length uncertainty.
    """
    global_unit_uncertainty_ref = int(arguments[2][0][1:])
    length_global_uncertainty = object_dict[global_unit_uncertainty_ref]
    return length_global_uncertainty


def vertex_point(arguments, object_dict):
    """
    Returns the data in case of a VERTEX.
    """
    return object_dict[arguments[1]]


def axis1_placement(arguments, object_dict):
    """
    Returns the data in case of a AXIS1_PLACEMENT.
    """
    return object_dict[arguments[1]], object_dict[arguments[2]]


def oriented_edge(arguments, object_dict):
    """
    Returns the data in case of an ORIENTED_EDGE.
    """
    edge_orientation = arguments[4]
    if edge_orientation == '.T.':
        return object_dict[arguments[3]]
    return object_dict[arguments[3]].reverse()


def face_outer_bound(arguments, object_dict):
    """
    Returns xx.

    :param arguments: DESCRIPTION
    :type arguments: TYPE
    :param object_dict: DESCRIPTION
    :type object_dict: TYPE
    :return: DESCRIPTION
    :rtype: TYPE

    """
    return object_dict[arguments[1]]


def face_bound(arguments, object_dict):
    """
    Returns xx.

    :param arguments: DESCRIPTION
    :type arguments: TYPE
    :param object_dict: DESCRIPTION
    :type object_dict: TYPE
    :return: DESCRIPTION
    :rtype: TYPE

    """
    return object_dict[arguments[1]]

# def surface_of_revolution(arguments, object_dict):


def surface_curve(arguments, object_dict):
    """
    Returns xx.

    :param arguments: DESCRIPTION
    :type arguments: TYPE
    :param object_dict: DESCRIPTION
    :type object_dict: TYPE
    :return: DESCRIPTION
    :rtype: TYPE

    """
    return object_dict[arguments[1]]


def seam_curve(arguments, object_dict):
    """
    Returns xx.

    :param arguments: DESCRIPTION
    :type arguments: TYPE
    :param object_dict: DESCRIPTION
    :type object_dict: TYPE
    :return: DESCRIPTION
    :rtype: TYPE
    """
    return object_dict[arguments[1]]


def trimmed_curve(arguments, object_dict):
    """
    Returns xx.

    :param arguments: DESCRIPTION
    :type arguments: TYPE
    :param object_dict: DESCRIPTION
    :type object_dict: TYPE
    :return: DESCRIPTION
    :rtype: TYPE
    """

    curve = object_dict[arguments[1]]
    point1 = object_dict[int(arguments[2][0][1:])]
    point2 = object_dict[int(arguments[3][0][1:])]
    return curve.trim(point1=point1, point2=point2)


def vertex_loop(arguments, object_dict):
    """
    Returns the data in case of a VERTEX_LOOP.
    """
    return object_dict[arguments[1]]


def pcurve(arguments, object_dict):
    """
    Returns the data in case of a PCURVE.
    """
    return object_dict[arguments[1]]


def geometric_curve_set(arguments, object_dict):
    """
    Returns xx.

    :param arguments: DESCRIPTION
    :type arguments: TYPE
    :param object_dict: DESCRIPTION
    :type object_dict: TYPE
    :return: DESCRIPTION
    :rtype: TYPE

    """
    sub_objects = []
    for argument in arguments[1]:
        sub_obj = object_dict[int(argument[1:])]
        sub_objects.append(sub_obj)
    return sub_objects


def shell_based_surface_model(arguments, object_dict):
    """
    Returns the data in case of a Shell3D.
    """
    return object_dict[int(arguments[1][0][1:])]


def item_defined_transformation(arguments, object_dict):
    """
    Returns xx.

    :param arguments: DESCRIPTION
    :type arguments: TYPE
    :param object_dict: DESCRIPTION
    :type object_dict: TYPE
    :return: DESCRIPTION
    :rtype: TYPE

    """
    # Frame3D
    volmdlr_object1 = object_dict[arguments[2]]
    volmdlr_object2 = object_dict[arguments[3]]
    # TODO : how to frame map properly from these two Frame3D ?
    # return volmdlr_object2 - volmdlr_object1
    return [volmdlr_object1, volmdlr_object2]


def manifold_surface_shape_representation(arguments, object_dict):
    """
    Returns the data in case of a manifold_surface_shape_representation, interpreted as shell3D.
    """
    shells = []
    for arg in arguments[1]:
        if isinstance(object_dict[int(arg[1:])],
                      volmdlr.faces.OpenShell3D):
            shell = object_dict[int(arg[1:])]
            shells.append(shell)
    return shells


def manifold_solid_brep(arguments, object_dict):
    """
    Returns the data in case of a manifold_solid_brep with voids.
    """
    return object_dict[arguments[1]]


def brep_with_voids(arguments, object_dict):
    """
    Returns the data in case of a BREP with voids.
    """
    return object_dict[arguments[1]]


def shape_representation(arguments, object_dict):
    """
    Returns xx.

    :param arguments: DESCRIPTION
    :type arguments: TYPE
    :param object_dict: DESCRIPTION
    :type object_dict: TYPE
    :return: DESCRIPTION
    :rtype: TYPE

    """
    # does it have the extra argument coming from
    # SHAPE_REPRESENTATION_RELATIONSHIP ? In this case
    # return them
    if len(arguments[:-1]) == 4:
        shells = object_dict[int(arguments[3])]
        return shells
    shells = []
    frames = []
    for arg in arguments[1]:
        if int(arg[1:]) in object_dict and \
                isinstance(object_dict[int(arg[1:])], list) and \
                len(object_dict[int(arg[1:])]) == 1:
            shells.append(*object_dict[int(arg[1:])])
        elif int(arg[1:]) in object_dict and \
                isinstance(object_dict[int(arg[1:])],
                           volmdlr.faces.OpenShell3D):
            shells.append(object_dict[int(arg[1:])])
        elif int(arg[1:]) in object_dict and \
                isinstance(object_dict[int(arg[1:])],
                           volmdlr.Frame3D):
            # TODO: Is there something to read here ?
            frame = object_dict[int(arg[1:])]
            if not all(component is None for component in [frame.u, frame.u, frame.w]):
                frames.append(frame)
        elif int(arg[1:]) in object_dict and \
                isinstance(object_dict[int(arg[1:])],
                           volmdlr.edges.Arc3D):
            shells.append(object_dict[int(arg[1:])])
        elif int(arg[1:]) in object_dict and \
                isinstance(object_dict[int(arg[1:])],
                           volmdlr.edges.BSplineCurve3D):
            shells.append(object_dict[int(arg[1:])])
        else:
            pass
    if not shells and frames:
        return frames
    return shells


def advanced_brep_shape_representation(arguments, object_dict):
    """
    Returns xx.

    :param arguments: DESCRIPTION
    :type arguments: TYPE
    :param object_dict: DESCRIPTION
    :type object_dict: TYPE
    :return: DESCRIPTION
    :rtype: TYPE

    """
    shells = []
    for arg in arguments[1]:
        if isinstance(object_dict[int(arg[1:])],
                      volmdlr.faces.OpenShell3D):
            shells.append(object_dict[int(arg[1:])])
    return shells


def frame_map_closed_shell(closed_shells, item_defined_transformation_frames, shape_representation_frames):
    """
    Frame maps a closed shell in an assembly to its good position.

    :param arguments: DESCRIPTION
    :type arguments: TYPE
    :param object_dict: DESCRIPTION
    :type object_dict: TYPE
    :return: DESCRIPTION
    :rtype: TYPE

    """
    if item_defined_transformation_frames[0] == item_defined_transformation_frames[1]:
        return closed_shells
    if shape_representation_frames[0].origin == volmdlr.O3D:
        global_frame = shape_representation_frames[0]
    else:
        global_frame = [frame for frame in item_defined_transformation_frames if frame.origin == volmdlr.O3D][0]
    transformed_frame = [frame for frame in item_defined_transformation_frames if frame != global_frame][0]
    new_closedshells = []

    for shell3d in closed_shells:
        basis_a = global_frame.basis()
        basis_b = transformed_frame.basis()
        A = npy.array([[basis_a.vectors[0].x, basis_a.vectors[0].y, basis_a.vectors[0].z],
                       [basis_a.vectors[1].x, basis_a.vectors[1].y, basis_a.vectors[1].z],
                       [basis_a.vectors[2].x, basis_a.vectors[2].y, basis_a.vectors[2].z]])
        B = npy.array([[basis_b.vectors[0].x, basis_b.vectors[0].y, basis_b.vectors[0].z],
                       [basis_b.vectors[1].x, basis_b.vectors[1].y, basis_b.vectors[1].z],
                       [basis_b.vectors[2].x, basis_b.vectors[2].y, basis_b.vectors[2].z]])
        transfer_matrix = npy.linalg.solve(A, B)
        u_vector = volmdlr.Vector3D(*transfer_matrix[0])
        v_vector = volmdlr.Vector3D(*transfer_matrix[1])
        w_vector = volmdlr.Vector3D(*transfer_matrix[2])
        new_frame = volmdlr.Frame3D(transformed_frame.origin, u_vector,
                                    v_vector,
                                    w_vector)
        new_faces = [face.frame_mapping(new_frame, 'old') for face in shell3d.faces]
        new_closed_shell3d = volmdlr.faces.ClosedShell3D(new_faces)
        new_closedshells.append(new_closed_shell3d)
    return new_closedshells


def representation_relationship_representation_relationship_with_transformation_shape_representation_relationship(
        arguments, object_dict):
    """
    Representation relationship with transformation shape. To clarify.
    """
    if arguments[2] in object_dict:
        if isinstance(object_dict[arguments[2]], list):  # arguments = {, , [], [], item_....}
            if object_dict[arguments[2]] and not isinstance(object_dict[arguments[2]][0], volmdlr.Frame3D)\
                          and isinstance(object_dict[arguments[3]][0], volmdlr.Frame3D):
                return frame_map_closed_shell(object_dict[arguments[2]],
                                              object_dict[arguments[4]], object_dict[arguments[3]])

            elif object_dict[arguments[2]] and isinstance(object_dict[arguments[2]][0], volmdlr.Frame3D) and\
                    not isinstance(object_dict[arguments[3]][0], volmdlr.Frame3D):
                return frame_map_closed_shell(object_dict[arguments[3]],
                                              object_dict[arguments[4]], object_dict[arguments[2]])
            return []
        return []
    return []


def bounded_curve_b_spline_curve_b_spline_curve_with_knots_curve_geometric_representation_item_rational_b_spline_curve_representation_item(
        arguments, object_dict):
    """
    Bounded b spline with knots curve geometric representation item. To clarify.
    """
    modified_arguments = [''] + arguments
    if modified_arguments[-1] == "''":
        modified_arguments.pop()
    return STEP_TO_VOLMDLR['BOUNDED_CURVE, '
                           'B_SPLINE_CURVE, '
                           'B_SPLINE_CURVE_WITH_KNOTS, '
                           'CURVE, GEOMETRIC_REPRESENTATION_ITEM, '
                           'RATIONAL_B_SPLINE_CURVE, '
                           'REPRESENTATION_ITEM'].from_step(
        modified_arguments, object_dict)


def bounded_surface_b_spline_surface_b_spline_surface_with_knots_geometric_representation_item_rational_b_spline_surface_representation_item_surface(
        arguments, object_dict):
    """
    Bounded b spline surface with knots curve geometric representation item. To clarify.
    """
    modified_arguments = [''] + arguments
    if modified_arguments[-1] == "''":
        modified_arguments.pop()
    return STEP_TO_VOLMDLR['BOUNDED_SURFACE, B_SPLINE_SURFACE, '
                           'B_SPLINE_SURFACE_WITH_KNOTS, '
                           'GEOMETRIC_REPRESENTATION_ITEM, '
                           'RATIONAL_B_SPLINE_SURFACE, '
                           'REPRESENTATION_ITEM, SURFACE'].from_step(
        modified_arguments, object_dict)


class StepFunction(dc.DessiaObject):
    """
    Abstract class defining a step function.

    """

    def __init__(self, function_id, function_name, function_arg):
        dc.DessiaObject.__init__(self)
        self.id = function_id
        self.name = function_name
        self.arg = function_arg

        # TODO : Modifier ce qui suit et simplify
        if self.name == "":
            if self.arg[1][0] == 'B_SPLINE_SURFACE':
                self.simplify('B_SPLINE_SURFACE')
            if self.arg[1][0] == 'B_SPLINE_CURVE':
                self.simplify('B_SPLINE_CURVE')
        dc.DessiaObject.__init__(self, name=function_name)

    def simplify(self, new_name):
        # ITERATE ON SUBFUNCTIONS
        args = [subfun[1] for (i, subfun) in enumerate(self.arg) if
                (len(subfun[1]) != 0 or i == 0)]
        arguments = []
        for arg in args:
            if not arg:
                arguments.append("''")
            else:
                arguments.extend(arg)
        arguments.pop()  # DELETE REPRESENTATION_ITEM('')

        self.name = new_name
        self.arg = arguments


class Step(dc.DessiaObject):
    """
    Defines the Step class.

    """

    def __init__(self, lines: List[str], name: str = ''):
        self.lines = lines
        self.functions, self.all_connections = self.read_lines()
        self._utd_graph = False
        self._graph = None
        self.global_uncertainty = 1e-6
        self.unit_conversion_factor = 1
        dc.DessiaObject.__init__(self, name=name)

    @property
    def graph(self):
        if not self._utd_graph:
            self._graph = self.create_graph()
            self._utd_graph = True
        return self._graph

    @classmethod
    def from_stream(cls, stream: BinaryFile = None):
        stream.seek(0)
        lines = []
        for line in stream:
            line = line.decode("ISO-8859-1")
            line = line.replace("\r", "")
            lines.append(line)
        return cls(lines)

    @classmethod
    def from_file(cls, filepath: str = None):
        with open(filepath, "r", encoding="ISO-8859-1") as file:
            lines = []
            for line in file:
                lines.append(line)
        return cls(lines)

    def read_lines(self):
        all_connections = []

        previous_line = ""
        functions = {}

        for line in self.lines:
            line = line.replace(" ", "")
            line = line.replace("\n", "")

            # SKIP EMPTY LINE
            if not line:
                continue

            # ASSEMBLE LINES IF THEY ARE SEPARATED
            if line[-1] != ';':
                previous_line = previous_line + line
                continue

            line = previous_line + line

            # SKIP HEADER
            if line[0] != "#":
                previous_line = str()
                continue

            function = line.split("=")
            function_id = int(function[0][1:])
            function_name_arg = function[1].split("(", 1)
            function_name = function_name_arg[0]
            function_arg = function_name_arg[1].split("#")
            function_connections = []
            # print(function_id, function_name)
            for connec in function_arg[1:]:
                connec = connec.split(",")
                connec = connec[0].split(")")
                if connec[0][-1] != "'":
                    function_connection = int(connec[0])
                    function_connections.append(
                        (function_id, function_connection))
            # print(function_connections)

            all_connections.extend(function_connections)

            previous_line = str()

            # FUNCTION ARGUMENTS
            function_arg = function_name_arg[1]
            arguments = step_split_arguments(function_arg)
            new_name = ''
            new_arguments = []
            if function_name == "":
                name_arg = self.step_subfunctions(arguments)
                for name, arg in name_arg:
                    new_name += name + ', '
                    new_arguments.extend(arg)
                new_name = new_name[:-2]
                function_name = new_name
                arguments = new_arguments
                for arg in arguments:
                    if arg[0] == '#':
                        function_connections.append(
                            (function_id, int(arg[1:])))
            # print('=', function_connections)

            for i, argument in enumerate(arguments):
                if argument[:2] == '(#' and argument[-1] == ')':
                    arg_list = set_to_list(argument)
                    arguments[i] = arg_list

            function = StepFunction(function_id, function_name, arguments)
            functions[function_id] = function

        return functions, all_connections

    def not_implemented(self):
        not_implemented = []
        for _, fun in self.functions.items():
            if fun.name not in STEP_TO_VOLMDLR:
                not_implemented.append(fun.name)
        return list(set(not_implemented))

    def create_graph(self):
        """
        Step functions graph
        :return:
        """
        G = nx.Graph()
        F = nx.DiGraph()
        labels = {}

        for function in self.functions.values():
            if function.name == 'SHAPE_REPRESENTATION_RELATIONSHIP':
                # Create short cut from id1 to id2
                id1 = int(function.arg[2][1:])
                id2 = int(function.arg[3][1:])
                elem1 = (function.id, id1)
                elem2 = (function.id, id2)
                self.all_connections.remove(elem1)
                self.all_connections.remove(elem2)
                self.all_connections.append((elem1[1], elem2[1]))

                self.functions[id1].arg.append('#{}'.format(id2))

            elif function.name in STEP_TO_VOLMDLR:
                G.add_node(function.id,
                           color='rgb(0, 0, 0)',
                           shape='.',
                           name=str(function.id))
                F.add_node(function.id,
                           color='rgb(0, 0, 0)',
                           shape='.',
                           name=str(function.id))
                labels[function.id] = str(function.id) + ' ' + function.name

        # Delete connection if node not found
        node_list = list(F.nodes())
        delete_connection = []
        for connection in self.all_connections:
            if connection[0] not in node_list \
                    or connection[1] not in node_list:
                delete_connection.append(connection)
        for delete in delete_connection:
            self.all_connections.remove(delete)

        # Create graph connections
        G.add_edges_from(self.all_connections)
        F.add_edges_from(self.all_connections)

        # Remove single nodes
        delete_nodes = []
        for node in F.nodes:
            if F.degree(node) == 0:
                delete_nodes.append(node)
        for node in delete_nodes:
            F.remove_node(node)
            G.remove_node(node)

        # if draw:
        #     # ----------------PLOT----------------
        #     pos = nx.kamada_kawai_layout(G)
        #     plt.figure()
        #     nx.draw_networkx_nodes(F, pos)
        #     nx.draw_networkx_edges(F, pos)
        #     nx.draw_networkx_labels(F, pos, labels)
        #     # ------------------------------------
        #
        # if html:
        #
        #     env = Environment(
        #         loader=PackageLoader('powertransmission', 'templates'),
        #         autoescape=select_autoescape(['html', 'xml']))
        #     template = env.get_template('graph_visJS.html')
        #
        #     nodes = []
        #     edges = []
        #     for label in list(labels.values()):
        #         nodes.append({'name': label, 'shape': 'circular'})
        #
        #     for edge in G.edges:
        #         edge_dict = {'inode1': int(edge[0]) - 1,
        #                      'inode2': int(edge[1]) - 1}
        #         edges.append(edge_dict)
        #
        #     options = {}
        #     s = template.render(
        #         name=self.stepfile,
        #         nodes=nodes,
        #         edges=edges,
        #         options=options)
        #
        #     with open('graph_visJS.html', 'wb') as file:
        #         file.write(s.encode('utf-8'))
        #
        #     webbrowser.open('file://' + os.path.realpath('graph_visJS.html'))

        return F

    def draw_graph(self, graph=None, reduced=False):
        """
        Draw a graph for Step data.

        :param graph: DESCRIPTION, defaults to None
        :type graph: TYPE, optional
        :param reduced: DESCRIPTION, defaults to False
        :type reduced: TYPE, optional
        :return: DESCRIPTION
        :rtype: TYPE

        """

        delete = ['CARTESIAN_POINT', 'DIRECTION']
        if graph is None:
            new_graph = self.create_graph()
        else:
            new_graph = graph.copy()

        labels = {}
        for id_nb, function in self.functions.items():
            if id_nb in new_graph.nodes and not reduced:
                labels[id_nb] = str(id_nb) + ' ' + function.name
            elif id_nb in new_graph.nodes and reduced:
                if function.name not in delete:
                    labels[id_nb] = str(id_nb) + ' ' + function.name
                else:
                    new_graph.remove_node(id_nb)
        pos = nx.kamada_kawai_layout(new_graph)
        plt.figure()
        nx.draw_networkx_nodes(new_graph, pos)
        nx.draw_networkx_edges(new_graph, pos)
        nx.draw_networkx_labels(new_graph, pos, labels)

    def step_subfunctions(self, subfunctions):
        subfunctions = subfunctions[0]
        parenthesis_count = 0
        subfunction_names = []
        subfunction_args = []
        subfunction_name = ""
        subfunction_arg = ""
        for char in subfunctions:

            if char == "(":
                parenthesis_count += 1
                if parenthesis_count == 1:
                    subfunction_names.append(subfunction_name)
                    subfunction_name = ""
                else:
                    subfunction_arg += char

            elif char == ")":
                parenthesis_count -= 1
                if parenthesis_count == 0:
                    subfunction_args.append(subfunction_arg)
                    subfunction_arg = ""
                else:
                    subfunction_arg += char

            elif parenthesis_count == 0:
                subfunction_name += char

            else:
                subfunction_arg += char
        return [
            (subfunction_names[i], step_split_arguments(subfunction_args[i]))
            for i in range(len(subfunction_names))]

    def parse_arguments(self, arguments):
        for i, arg in enumerate(arguments):
            if isinstance(arg, str) and arg[0] == '#':
                arguments[i] = int(arg[1:])
            elif isinstance(arg, str) and arg[0:2] == '(#':
                argument = []
                arg_id = ""
                for char in arg[1:-1]:
                    if char == ',':
                        argument.append(arg_id)
                        arg_id = ""
                        continue

                    arg_id += char
                argument.append(arg_id)
                arguments[i] = argument

    def instanciate(self, name, arguments, object_dict):
        """
        Gives the volmdlr object related to the step function.
        """
        self.parse_arguments(arguments)

        fun_name = name.replace(', ', '_')
        fun_name = fun_name.lower()
        if hasattr(volmdlr.step, fun_name):
            volmdlr_object = getattr(volmdlr.step, fun_name)(arguments, object_dict)

        elif name in STEP_TO_VOLMDLR and hasattr(STEP_TO_VOLMDLR[name], "from_step"):
            volmdlr_object = STEP_TO_VOLMDLR[name].from_step(arguments, object_dict)

        else:
            raise NotImplementedError(
                'Dont know how to interpret {} with args {}'.format(name,
                                                                    arguments))
        return volmdlr_object

    def to_volume_model(self, show_times: bool = False):
        """
        show_times=True displays the number of times a given class has been
        instantiated and the total time of all the instantiations of this
        given class.
        """

        object_dict = {}

        self.graph.add_node("#0")
        frame_mapping_nodes = []
        shell_nodes = []
        unit_measure_nodes = []
        length_global_uncertainty_node = None
        conversion_factor_node = None
        # sr_nodes = []
        not_shell_nodes = []
        assembly_nodes = []
        for node in self.graph.nodes:
            if node != '#0' and self.functions[node].name == 'REPRESENTATION_RELATIONSHIP, REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION, SHAPE_REPRESENTATION_RELATIONSHIP':
                frame_mapping_nodes.append(node)
            if node != '#0' and (self.functions[node].name in ["CLOSED_SHELL", "OPEN_SHELL"]):
                shell_nodes.append(node)
            if node != '#0' and self.functions[node].name == 'REPRESENTATION_RELATIONSHIP_REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION_SHAPE_REPRESENTATION_RELATIONSHIP':
                assembly_nodes.append(node)
            # if node != '#0' and self.functions[node].name in [
            #     'UNCERTAINTY_MEASURE_WITH_UNIT', 'LENGTH_UNIT, NAMED_UNIT, SI_UNIT']:
            #     unit_measure_nodes.append(node)
            if node != '#0' and not length_global_uncertainty_node and self.functions[node].name ==\
                    'UNCERTAINTY_MEASURE_WITH_UNIT':
                length_global_uncertainty_node = node
            # if node != '#0' and self.functions[node].name == 'SHAPE_REPRESENTATION':
            #     # Really a shell node ?
            #     sr_nodes.append(node)
            if node != '#0' and self.functions[node].name == 'BREP_WITH_VOIDS':
                shell_nodes.append(node)
                not_shell_nodes.append(int(self.functions[node].arg[1][1:]))
        frame_mapped_shell_node = []
        for s_node in shell_nodes:
            for fm_node in frame_mapping_nodes:
                if nx.has_path(self.graph, source=fm_node, target=s_node):
                    frame_mapped_shell_node.append(s_node)
                    break
        shell_nodes_copy = shell_nodes.copy()
        remove_nodes = list(set(frame_mapped_shell_node + not_shell_nodes))
        for node in remove_nodes:
            shell_nodes.remove(node)

        for node in shell_nodes + frame_mapping_nodes:
            self.graph.add_edge('#0', node)

        # self.draw_graph(self.graph, reduced=True)

        nodes = []
        i = 1
        new_nodes = True
        while new_nodes:
            new_nodes = list(nx.descendants_at_distance(self.graph, '#0', i))[::-1]
            nodes.extend(new_nodes)
            i += 1

        # nodes = dessia_common.graph.explore_tree_from_leaves(self.graph)

        times = {}
        for i, node in enumerate([length_global_uncertainty_node] + nodes[::-1]):
            # instanciate_ids = [edge[1]]
            if node is None:
                continue
            instanciate_ids = [node]
            error = True
            while error:
                try:
                    for instanciate_id in instanciate_ids[::-1]:
                        t = time.time()
                        arguments = self.functions[instanciate_id].arg[:]
                        volmdlr_object = self.instanciate(
                            self.functions[instanciate_id].name,
                            self.functions[instanciate_id].arg[:] + [self.unit_conversion_factor], object_dict)
                        t = time.time() - t
                        object_dict[instanciate_id] = volmdlr_object
                        if show_times:
                            if volmdlr_object.__class__ not in times:
                                times[volmdlr_object.__class__] = [1, t]
                            else:
                                times[volmdlr_object.__class__][0] += 1
                                times[volmdlr_object.__class__][1] += t
                    error = False
                except KeyError as key:
                    # Sometimes the bfs search don't instantiate the nodes of a
                    # depth in the right order, leading to error
                    instanciate_ids.append(key.args[0])
            if i == 0:
                self.global_uncertainty = volmdlr_object
                self.unit_conversion_factor = object_dict[int(arguments[1][1:])]

        if show_times:
            print()
            for key, value in times.items():
                print(f'| {key} : {value}')
            print()

        shells = []
        if frame_mapping_nodes:
            for node in frame_mapping_nodes:
                shells.extend(object_dict[node])
        if not shells:
            for node in shell_nodes_copy:
                if isinstance(object_dict[node], list):
                    shells.extend(object_dict[node])
                else:
                    shells.append(object_dict[node])
        volume_model = volmdlr.core.VolumeModel(shells)
        # bounding_box = volume_model.bounding_box
        # volume_model = volume_model.translation(-bounding_box.center)
        return volume_model

    def to_points(self):
        object_dict = {}
        points3d = []
        for stepfunction in self.functions.values():
            if stepfunction.name == 'CARTESIAN_POINT':
                # INSTANTIATION
                name = self.functions[stepfunction.id].name
                arguments = self.functions[stepfunction.id].arg[:]
                self.parse_arguments(arguments)
                # for i, arg in enumerate(arguments):
                #     if type(arg) == str and arg[0] == '#':
                #         arguments[i] = int(arg[1:])
                # print(arguments)
                if arguments[1].count(',') == 2:
                    volmdlr_object = STEP_TO_VOLMDLR[name].from_step(
                        arguments, object_dict)
                    points3d.append(volmdlr_object)

        # remove first point because it refers to origin
        return points3d[1:]

    def plot_data(self):
        graph = self.graph.copy()

        graph.remove_nodes_from([stepfunction.id for stepfunction
                                 in self.functions.values()
                                 if stepfunction.name in ['CARTESIAN_POINT', 'DIRECTION']])
        return [plot_data.graph.NetworkxGraph(graph=graph)]


STEP_TO_VOLMDLR = {
    # GEOMETRICAL ENTITIES
    'CARTESIAN_POINT': volmdlr.Point3D,
    'DIRECTION': volmdlr.Vector3D,
    'VECTOR': volmdlr.Vector3D,

    'AXIS1_PLACEMENT': None,
    'AXIS2_PLACEMENT_2D': None,  # ??????????????????
    'AXIS2_PLACEMENT_3D': volmdlr.Frame3D,

    'LINE': volmdlr.edges.Line3D,  # LineSegment3D,
    'CIRCLE': volmdlr.wires.Circle3D,
    'ELLIPSE': volmdlr.wires.Ellipse3D,
    'PARABOLA': None,
    'HYPERBOLA': None,
    # 'PCURVE': None,
    'CURVE_REPLICA': None,
    'OFFSET_CURVE_3D': None,
    'TRIMMED_CURVE': None,  # BSplineCurve3D cannot be trimmed on FreeCAD
    'B_SPLINE_CURVE': volmdlr.edges.BSplineCurve3D,
    'B_SPLINE_CURVE_WITH_KNOTS': volmdlr.edges.BSplineCurve3D,
    'BEZIER_CURVE': volmdlr.edges.BSplineCurve3D,
    'RATIONAL_B_SPLINE_CURVE': volmdlr.edges.BSplineCurve3D,
    'UNIFORM_CURVE': volmdlr.edges.BSplineCurve3D,
    'QUASI_UNIFORM_CURVE': volmdlr.edges.BSplineCurve3D,
    'SURFACE_CURVE': None,  # TOPOLOGICAL EDGE
    'SEAM_CURVE': None,
    # LineSegment3D, # TOPOLOGICAL EDGE ############################
    'COMPOSITE_CURVE_SEGMENT': None,  # TOPOLOGICAL EDGE
    'COMPOSITE_CURVE': volmdlr.wires.Wire3D,  # TOPOLOGICAL WIRE
    'COMPOSITE_CURVE_ON_SURFACE': volmdlr.wires.Wire3D,  # TOPOLOGICAL WIRE
    'BOUNDARY_CURVE': volmdlr.wires.Wire3D,  # TOPOLOGICAL WIRE

    'PLANE': volmdlr.faces.Plane3D,
    'CYLINDRICAL_SURFACE': volmdlr.faces.CylindricalSurface3D,
    'CONICAL_SURFACE': volmdlr.faces.ConicalSurface3D,
    'SPHERICAL_SURFACE': volmdlr.faces.SphericalSurface3D,
    'TOROIDAL_SURFACE': volmdlr.faces.ToroidalSurface3D,
    'DEGENERATE_TOROIDAL_SURFACE': None,
    'B_SPLINE_SURFACE_WITH_KNOTS': volmdlr.faces.BSplineSurface3D,
    'B_SPLINE_SURFACE': volmdlr.faces.BSplineSurface3D,
    'BEZIER_SURFACE': volmdlr.faces.BSplineSurface3D,
    'OFFSET_SURFACE': None,
    'SURFACE_REPLICA': None,
    'RATIONAL_B_SPLINE_SURFACE': volmdlr.faces.BSplineSurface3D,
    'RECTANGULAR_TRIMMED_SURFACE': None,
    'SURFACE_OF_LINEAR_EXTRUSION': volmdlr.primitives3d.BSplineExtrusion,
    # CAN BE A BSplineSurface3D
    'SURFACE_OF_REVOLUTION': volmdlr.faces.RevolutionSurface3D,
    'UNIFORM_SURFACE': volmdlr.faces.BSplineSurface3D,
    'QUASI_UNIFORM_SURFACE': volmdlr.faces.BSplineSurface3D,
    'RECTANGULAR_COMPOSITE_SURFACE': volmdlr.faces.PlaneFace3D,  # TOPOLOGICAL FACES
    'CURVE_BOUNDED_SURFACE': volmdlr.faces.PlaneFace3D,  # TOPOLOGICAL FACE

    # Bsplines
    'BOUNDED_SURFACE, B_SPLINE_SURFACE, B_SPLINE_SURFACE_WITH_KNOTS, GEOMETRIC_REPRESENTATION_ITEM, RATIONAL_B_SPLINE_SURFACE, REPRESENTATION_ITEM, SURFACE': volmdlr.faces.BSplineSurface3D,

    # TOPOLOGICAL ENTITIES
    'VERTEX_POINT': None,

    'EDGE_CURVE': volmdlr.edges.Edge,  # LineSegment3D, # TOPOLOGICAL EDGE
    'ORIENTED_EDGE': None,  # TOPOLOGICAL EDGE
    # The one above can influence the direction with their last argument
    # TODO : maybe take them into consideration

    'FACE_BOUND': None,  # TOPOLOGICAL WIRE
    'FACE_OUTER_BOUND': None,  # TOPOLOGICAL WIRE
    # Both above can influence the direction with their last argument
    # TODO : maybe take them into consideration
    'EDGE_LOOP': volmdlr.wires.Contour3D,  # TOPOLOGICAL WIRE
    'POLY_LOOP': volmdlr.wires.Contour3D,  # TOPOLOGICAL WIRE
    'VERTEX_LOOP': None,  # TOPOLOGICAL WIRE

    'ADVANCED_FACE': volmdlr.faces.Face3D,
    'FACE_SURFACE': volmdlr.faces.Face3D,

    'CLOSED_SHELL': volmdlr.faces.ClosedShell3D,
    'OPEN_SHELL': volmdlr.faces.OpenShell3D,
    #        'ORIENTED_CLOSED_SHELL': None,
    'CONNECTED_FACE_SET': volmdlr.faces.OpenShell3D,
    'GEOMETRIC_CURVE_SET': None,

    # step subfunctions
    'UNCERTAINTY_MEASURE_WITH_UNIT': None,
    'CONVERSION_BASED_UNIT, LENGTH_UNIT, NAMED_UNIT': None,
    'LENGTH_MEASURE_WITH_UNIT': None,
    'LENGTH_UNIT, NAMED_UNIT, SI_UNIT': None,
    'GEOMETRIC_REPRESENTATION_CONTEXT, GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT, GLOBAL_UNIT_ASSIGNED_CONTEXT, REPRESENTATION_CONTEXT': None,
    'REPRESENTATION_RELATIONSHIP, REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION, SHAPE_REPRESENTATION_RELATIONSHIP': volmdlr.faces.OpenShell3D.translation,
    'SHELL_BASED_SURFACE_MODEL': None,
    'MANIFOLD_SURFACE_SHAPE_REPRESENTATION': None,
    'MANIFOLD_SOLID_BREP': None,
    'BREP_WITH_VOIDS': None,
    'SHAPE_REPRESENTATION': None,
    'ADVANCED_BREP_SHAPE_REPRESENTATION': None,
    'ITEM_DEFINED_TRANSFORMATION': None,
    'SHAPE_REPRESENTATION_RELATIONSHIP': None,

    'BOUNDED_CURVE, B_SPLINE_CURVE, B_SPLINE_CURVE_WITH_KNOTS, CURVE, GEOMETRIC_REPRESENTATION_ITEM, RATIONAL_B_SPLINE_CURVE, REPRESENTATION_ITEM': volmdlr.edges.BSplineCurve3D
}

VOLMDLR_TO_STEP = {}
for k, v in STEP_TO_VOLMDLR.items():
    if v:
        if v in VOLMDLR_TO_STEP:
            VOLMDLR_TO_STEP[v].append(k)
        else:
            VOLMDLR_TO_STEP[v] = [k]

SI_PREFIX = {'.EXA.': 1e18, '.PETA.': 1e15, '.TERA.': 1e12, '.GIGA.': 1e9, '.MEGA.': 1e6, '.KILO.': 1e3,
             '.HECTO.': 1e2, '.DECA.': 1e1, '$': 1, '.DECI.': 1e-1, '.CENTI.': 1e-2, '.MILLI.': 1e-3, '.MICRO.': 1e-6,
             '.NANO.': 1e-9, '.PICO.': 1e-12, '.FEMTO.': 1e-15, '.ATTO.': 1e-18}

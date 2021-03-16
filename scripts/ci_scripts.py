
import os

scripts = ['arcs2D.py', 'arcs3D.py', 'block3d.py', 'simple_shapes.py',
           'roundedlines.py','polygon2D.py', 'polygon2D_2.py',
           'primitives/extrusion.py', 'demo2D.py', 'showcases/casing.py', 'sweep.py',
           'primitives/revolved_profile.py', 'edges/areas_moment_cog_check.py']

for script_name in scripts:
    print('\n## Executing script {}'.format(script_name))

    exec(open(script_name).read())

# TODO: port these commented scripts!
distance_scripts = ['arc3D_arc3D.py','arc3D_ls3D.py',
                   #  'cyl_cyl.py', 'cyl_pf.py',
                   # 'ls3D_ls3D.py', 'sweep_sweep.py', 'tore_cyl.py','tore_pf.py'
                   # 'tore_tore.py'
                    ]

for script_name in distance_scripts:
    print('\n## Executing script {}'.format(script_name))
    exec(open(os.path.join('distance', script_name)).read())

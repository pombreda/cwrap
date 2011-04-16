import os
import subprocess
import tempfile

import parser 
import renderers

    
def _parse(header, include_dirs):
    """ Parse the given header file into and ast. The include
    dirs are passed along to gccxml.

    """
    # A temporary file to store the xml generated by gccxml
    xml_file = tempfile.NamedTemporaryFile(suffix='.xml', delete=False)
    xml_file.close()

    # buildup the gccxml command
    cmds = ['gccxml']
    for inc_dir in include_dirs:
        cmds.append('-I' + inc_dir)
    cmds.append(header.path)
    cmds.append('-fxml=%s' % xml_file.name)
    
    # we pipe stdout so the preprocessing doesn't dump to the 
    # shell. We really don't care about it.
    p = subprocess.Popen(cmds, stdout=subprocess.PIPE)
    cpp, _ = p.communicate()
    
    # Parse the xml into the ast then delete the temp file
    ast = parser.parse(xml_file.name)
    os.remove(xml_file.name)

    return ast


def _render_extern(ast, header, config):
    renderer = renderers.ExternRenderer()
    return renderer.render(ast, header.path, config)


def generate(config):
    save_dir = config.save_dir
    include_dirs = config.include_dirs
    for header in config.headers:
        items = _parse(header, include_dirs)
        extern_code = _render_extern(items, header, config)
        extern_path = os.path.join(save_dir, header.pxd + '.pxd')
        with open(extern_path, 'wb') as f:
            f.write(extern_code)



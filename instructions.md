# (WIP) Task - Build LDraw models from source 

**Build me** a `.mpd` source file for a **LDraw model**, you **decide** both about the **model kind** and its **features**.

## Tooling

Use the following **available tools** (TODO complete list with agentic generated tooling):

- `leocad`: this is actually a LDraw CAD editor, but **also a CLI tool**. Run with `leocad --help` for options help.
    - **NOTE:** The `-l` option should be always set as: `leocad -l $LDRAW_DIR <other params>`
- `ldview`: a LDraw model viewer, for me to **inspect the final result**, to be run as: `ldview <model.mpd> &`
    - **NOTE:** Use this tool **only as instructed**, it doesn't produce any stdout/stderr output, and doing otherwise could cause for the viewer to open and pause the pipeline execution until the viewer is either closed or killed.
- `./check-model.sh`: To be run **before** `ldview`, shows the **same errors** as LDView would when opening a file, this will give you a **chance to fix extra errors** that could affect the final rendering for the model. Run as: `./check-model.sh <model.mpd>`
- `./prepare-glb.sh`: To be run when in need of **converting** a `.mpd`, `.dat` or `.ldr` model or part files **into a `.glb` model with semantic annotations** added as custom properties. 
    - **NOTE:** The **intended use case** for this tool is to **load the generated model or part in Blender headless** via **MCP**, in order to use **Blender tooling** for **geometrical and structural correctness feedback**, also taking advantage inside Blender of the **extra Custom Properties** added for **semantic interpretation** of the model **structure** and its different parts.
- **TODO add more agentic tool items to this list**

## Resources

**TODO add informational resources here, in order to enable the agent to retrieve useful and required information for its task, like e.g. markdown API documentation, LDraw standard reference docs, etc.**


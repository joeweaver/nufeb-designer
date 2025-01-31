# About nufeb-designer
Graphical User Interface for creating NUFEB simulation configurations

NUFEB (Newcastle University Frontier in Engineering Biology) is an open source tool for 3D agent-based simulation of microbial systems. The tool is built on top of the molecular dynamic simulator LAMMPS, and extended with features for microbial modelling. As part of this legacy, the inputs to NUFEB are rooted in terms more familiar to molecular dynamics simulations.

Nufeb-designer is a graphical user interface frontend which enables creating NUFEB configurations, including initial organism layouts, at a high level of abstraction and  without needing to understand the configuration language.

Development was funded by the US NSF Postdoctoral Research Fellowship in Biology Award #2007151.

Because nufeb-deisgner is under active development and experimental, we would like you contact us if you use it. We'd enjoy hearing about how we could make it better AND we'd like to have a list of people to contact if major bugs are found. The best person to contact at this time would be Joseph E. Weaver: joe.weaver@newcastle.ac.uk  Pleas also feel free to file an [issue](https://github.com/joeweaver/nufeb-designer/issues).

# Getting Started

nufeb-designer was written with Python 3.11 and has a major dependency of ``pyqt6``

It also requires a local install of the [nufebmgr](https://github.com/joeweaver/nufebmgr) package, which is used to generate NUFEB input files. nufebmgr depends on:

* numpy 2.2.0
* pandas 2.2.0
* jinja2 3.1.0
* opencv-python 4.9.0

A working installation of [NUFEB](https://github.com/nufeb/NUFEB-2) is not required to use nufeb-designer, but generating input files for NUFEB would be rather pointless without it.

nufeb-designer can be simply cloned from git, but before running it the first time, you must use the QT utilty ``pyuic6`` to generate some python files related to the UI.  ``pyuic6`` should already be installed if you have met the ``pyqt6`` requirement.

From the top-level directory run ``pyuic6 -x ./ui -o ./src``.  If you are working on the nufeb-designer code and with Pycharm, you may want to set up a before-launch/external tool run configuration which automatically runs this each time.

To run nufeb-designer, ``python ./src/nufeb-designer.py``

# Overview

nufeb-designer has one main window largely devoted to placing the initial bacterial positions and assigning their taxa. Once a valid layout is created, the ``Generate NUFEB Inputs`` button will be activated, allowing you to write an ``atom.in`` and ``inputscript.nufeb`` file to a selected directory. These are two files which define a NUFEB simulation.

<p>
  <img src="https://github.com/joeweaver/nufeb-designer/blob/main/doc/images/ui_overview.png" width=500>
</p>

## Layouts and distributions

The large white area on the right represents the plane where initial bacteria will be located. Its dimensions can be altered using the dimension text boxes at the top and it will, when appropriate, try to stretch to fit the drawing area.  

Individual bacteria can be placed by left clicking in the drawing area and erased by right clicking. By default placed locations will have a black colour indicating they have no assigned taxon.

You can also bulk-add bacterial locations using three difference layout options.

* An entirely random layout consisting of *n* bacteria

<p>
  <img src="https://github.com/joeweaver/nufeb-designer/blob/main/doc/images/random_200.png" width=250>
</p>
  
* A poisson-disc random layout which enforces a minimum distance between bacteria.

<p>
  <img src="https://github.com/joeweaver/nufeb-designer/blob/main/doc/images/poisson_5.png" width=250>
</p>
  
* A grid layout with *m* rows and *n* columns

<p>
  <img src="https://github.com/joeweaver/nufeb-designer/blob/main/doc/images/grid_4x3.png" width=250>
</p>

It is also possible to use the ``clear points`` button to remove all current locations.

## Taxa

Taxa area loaded using json files which define taxa libraries. The nufebmgr README defines this format, but you'll also be able to edit them in nufeb-designer.

There is a simple default library already loaded, and its contents (along with the associated colour codes) is displayed in the table to the lower left. Clicking a taxon in this table will change the colour of pen in the drawing area - any newly placed points, including with the layout buttons, will be assigned that taxon automatically.

Taxa assignments can also be cleared using the ``Clear Taxa Assignment`` button, all existing locations will be kept but set to 'unassigned taxa' status and appear black.

You can assign random points to taxa with an even population balance using the the ``Evenly`` button.  If you don't want even proportions, you can click ``Specify Proportion`` button to fill out which proportions you'd like (these are automatically normalized to add to 1).

<p>
  <img src="https://github.com/joeweaver/nufeb-designer/blob/main/doc/images/assign_taxa.png" width=250>
</p>


### Editing and Managing Taxa Libraries

The ``Load/Edit Taxa Button`` and menu item under ``Taxa Manager`` allows you to edit the currently loaded taxa, load a different taxa library, or save the current edits to a new taxa library file.

It brings up a dialog with two tables. The top table is an overview of each taxon and double clicking on the parameters allows them to be edited. Additionally, the growth strategy of the highlighted taxon is shown and is editable in the bottom table.  New taxa can be added to the list with the ``Add`` and ``Duplicate`` buttons. Taxa can also be removed with remove ``Button``.

To save your edits for another session,  you can use the ``Save to File`` button to create a json taxa library file.  This file can then be loaded in later sessions with the ``Load from File`` button.

<p>
  <img src="https://github.com/joeweaver/nufeb-designer/blob/main/doc/images/taxa_library.png" width=700>
</p>

## Type VI Secretion Interactions

To add a Type VI Secretion System to the simulation, use the ``Interactions->Type VI Secretion`` menu item.  This brings up a dialog where you specify attacker/vulnerable pairs in a table.  This UI has been designed to provide the simplest possible way to add T6SS interactions.

To specify a pair, click the ``Add Pair`` button then select the attacker and vulnerable taxon from the dropdown boxes in each column.

<p>
  <img src="https://github.com/joeweaver/nufeb-designer/blob/main/doc/images/t6ss.png" width=250>
</p>

## Other simulation settings

It is also possible to specify the simulation run time and random number generator seed.

## Generation

To generate a NUFEB case, simply press the ``Generate NUFEB Inputs`` button. You will be prompted where to save the generated case definition files. From there, you can use them as you would normally with NUFEB.  The most likely reason the button is not enabled is either because there are points with unassigned taxa or, more rarely, and invalid input setting (which should be highlighted with a red outline).

# Limitations

To constrain context nufeb-designer was largely developed by 'dogfooding' based on the needs of the cases specific to the developer's research. As such, it is particularly good at setting up Type VI Secretion System simulations and is currently suitable for generating simulations involving cocci but not the more recent bacillus morphology. It has been generally tested with classic Monod-style heterotrophic growth. Other growth strategies have not been as exhaustively tested.

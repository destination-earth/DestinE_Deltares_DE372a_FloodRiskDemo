Generic Adaptation Modelling Framework Demonstrator
===================================================

This package implements the Generic Adaptation Modelling Framework (GAMF) developed in the Destination Earth 372 project Lot 1 for flood events. It provides a user interface built using [solara](https://solara.dev/) to interact with the [FloodAdapt](https://github.com/Deltares-research/FloodAdapt) backend.
#### **Warning**:
This demonstrator is a **prototype**. Not all FloodAdapt functionality is implemented.  
To make full use of the demonstrator, a [FloodAdapt database]([https://github.com/Deltares-research/FloodAdapt?tab=readme-ov-file#configure-database](https://deltares-research.github.io/FloodAdapt/3_setup_guide/database.html)) is needed. To help set one up, or be provided with an example, please contact *\<insert contact person\>*. Essential to a FloodAdapt database are working [SFINCS](https://sfincs.readthedocs.io/en/latest/) and [Delft-FIAT](https://www.deltares.nl/en/software-and-data/products/delft-fiat-flood-impact-assessment-tool) models for flood extent/water depth and damage calculations. To set up those models, or update existing models, please consult [here](https://github.com/Deltares/hydromt_sfincs) for SFINCS and [here](https://github.com/Deltares/hydromt_fiat) for Delft-FIAT (experience or familiarity with the respective models recommended). To set up a FloodAdapt database around pre-existing SFINCS and Delft-FIAT models, please consult [here](https://deltares-research.github.io/FloodAdapt/3_setup_guide/database.html#configuration-file-attributes) Model executables are assumed to be part of the FloodAdapt database under the `system` directory. To change this location, adapt the `Settings` in the `demonstrator/front.py` file. To change where the FloodAdapt database itself is located, adapt the `app.py` file. Some familiarity with FloodAdapt is recommended when using this demonstrator.


Installation
------------------------

To manage the python environment we recommend using [mamba](https://mamba.readthedocs.io/en/latest/), a faster alternative to conda, which comes with the [miniforge](https://conda-forge.org/download/) distribution. Note that the demonstrator package is not available on PyPi or conda-forge, so the demonstrator needs to be installed from the GitHub repository. This requires [git](https://git-scm.com/) to be installed. The following snippet clones the repository, checks out the correct branch, and creates and activates the conda environment.

```bash
git clone git@github.com:interTwin-eu/DT-flood.git
cd DT-flood
git checkout de372
cd Demonstrator
mamba env create -f environment.yml
mamba activate de372
```

The demonstrator does not rely on any other components in the DT-flood repository that are not in this directory. So an alternative to the above installation instructions that does not also clone the rest of the DT-flood repository to your machine is to do the following:

```bash
git clone git@github.com:interTwin-eu/DT-flood.git --no-checkout DT-flood
cd DT-flood
git sparse-checkout init
git sparse-checkout add Demonstrator
git checkout de372
cd Demonstrator
mamba env create -f environment.yml
mamba activate de372
```

Running the Demonstrator
------------------------

With the `de372` environment activated, the demonstrator is launched by calling `solara run app.py` on the command line. The demonstrator will then run on `localhost:8765` which will open automatically in your browser.

Using the Demonstrator
----------------------

The interface is split into two sections: an interactive map as the main section and various tabs for configuring FloodAdapt scenarios in the sidebar.

### Interactive Map

The interactive map allows the user to loop around the area for which the FloodAdapt database is configured. When the relevant tabs in the sidebar are selected, tools are available to draw lines or polygons or place markers on the map. Below the map is a dropdown menu listing scenarios that have succesfully run. Selecting a scenario allows the user to plot various outputs on the map (or in the case of metrics, below the map). Note that rendering the plots may take some time depending on the size of the output. Switching tabs on the right does not reset rendering the plots, though it is recommended to disable the plots before switching tabs as the performance may suffer with plots enabled.

### Configuration Tabs

The tabs in the sidebar allow a user to configure everything needed to create and run a FloodAdapt scenario. For more details on Events, Projections, Measures, and Strategies that make up a Scenario, please consult the [FloodAdapt documentation](https://deltares-research.github.io/FloodAdapt/). Here we run through the functionalities of the corresponding tabs specific to the demonstrator.

#### 1. Events

This tab allows a user to configure an event that is to be run as part of a scenario. Currently, only the Synthetic event type is supported. Once an event type has been selected, options to further specify the event timing and forcing are opened. As an event can consist of multiple meteorological forcings, the demonstrator keeps track of a list of user configured forcings at the bottom of the tab before saving to the database. The `Add Forcing` button adds to this list, and thus does not save anything to the database itself. There can be only one forcing of each type in this list. Adding a forcing of an existing type will overwrite the respective forcing in the list. Once an event has been fully specified, the `Save Event` button will save it to the database for later use.

#### 2. Projections

This tab allows a user to configure a projection that modifies parts of either the event simulation or the damage calculation. The current available options are sea level rise and rainfall increase for the event simulation and overall population increase and economic growth for the damage calculation. Once a projection has been fully specified, the `Save Projection` button will save it to the database for later use.

#### 3. Measures

This tab allows a user to configure a measure to be part of the strategy that is applied to the scenario. Accessing this tab enables tools to draw on the interactive map. At the bottom of the tab is displayed what the current active geometry is that will accompany the measure configuration. Note that only one geometry can be active despite multiple being drawn on the map. Also note that a check whether the active geometry type is compatible with the selected measure type happens only when saving the measure. Once a measure has been fully specified, the `Save Measure` button will save it to the database for later use.

#### 4. Strategy

This tab allows a user to configure a strategy to apply during a scenario. The tab lists all measures recognized by the database as valid with checkboxes for a user to indicate which measures should be part of the new strategy. Once a strategy has been fully specified, the `Save Strategy` button will save it to the database for later use.

#### 5. Scenario

This tab allows a user to configure a new scenario by specifying one of each of an event, a projection, and a strategy. Valid choices are made available through the dropdown menus. Once a scenario has been fully specified, the `Save Scenario` button will save it ot the database for later use.

#### 6. Run

This tab allows a user to execute a previously defined scenario by selecting a valid scenario from the dropdown menu and pressing the `Run Scenario` button. Any feedback or logging by FloodAdapt or the models themselves are printed to the terminal from which the demonstrator was launched. Once a scenario has been succesfully run, it becomes available in the dropdown menu below the map on the left for plotting the output.

Destination Earth Climate DT Data
---------------------------------

The notebook `dt-climate-data.ipynb` provides an example of how to download DT Climate data using [earthkit](https://earthkit.readthedocs.io/en/latest/index.html) and [polytope](https://polytope.readthedocs.io/en/latest/) and some basic processing for usage by [HydroMT](https://github.com/Deltares/hydromt) or FloodAdapt (which uses HydroMT in the backend). Using this notebook requires prior authentication using the `desp-authentication.py` script or through a token in the file `~/polytopeapirc` (which the authentication script creates). See [here](https://github.com/destination-earth-digital-twins/polytope-examples) for more details and further examples of working with DT Climate data.

The process of downloading and processing DT Climate data, and prepare them in a FloodAdapt event is not part of the demonstrator proper. Downloading and processing the data (especially interpolating to a regulat lat-lon grid) can take some time. This breaks the interactive nature of the demonstrator and FloodAdapt. Instead we advice to prepare the the desired data files beforehand and use FloodAdapt/the demonstrator to quickly run and inspect scenarios which use the pre-prepared data files. For rainfall and wind there are options to build events using user-specified csv files. However, coastal waterlevels and river discharges are not part of the DT Climate datasets. To use DT Climate data in scenarios / areas where these two forcing types are relevant or dominant, coastal hydrodynamics / hydrological models forced with DT Climate data need to run first. It is up to the user to do this before using the demonstrator.
#### **Warning**:
Using DT Climate precipation, winds, and mean sea level pressure together with coastal waterlevels from a different source is dynamically inconsistent and may lead to inaccurate / physically incorrect results.

 

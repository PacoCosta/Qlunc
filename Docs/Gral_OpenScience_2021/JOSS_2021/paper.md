---
title: 'Qlunc: A Python package for quantification of lidar uncertainty'
tags:
  - wind lidar
  - lidar hardware uncertainty
  - OpenScience
  - OpenLidar
authors:
  - name: Francisco Costa García
    orcid: 0000-0003-1318-9677
    affiliation: 1
affiliations:
 - name: University of Stuttgart. Institute for Aircraft Design - SWE
   index: 1
date: 25 February 2021
bibliography: paper.bib
---

# Summary

``Qlunc``, for Quantification of lidar uncertainty, is an open-source, freely available
(https://github.com/SWE-UniStuttgart/Qlunc) python-based tool that aims to estimate
the uncertainty of a wind lidar device, including hardware and data processing methods.
Based on the OpenLidar architecture [@OpenLidar], it contains models of the uncertainty contributed
by individual lidar components and modules, that are then combined to estimate the total
uncertainty of the lidar device.

The code is meant to be as modular as possible, easily allowing lidar components’ (represented
by python objects) interchangeability and outcomes’ repeatability.
Furthermore, it allows to easily integrate different uncertainty methods or interface
external codes. ``Qlunc`` has an objected-oriented structure taking advantage of python
features; by using python objects and simulating real lidar components, the code puts all
together in modules and, eventually builds up a lidar digital twin.
This, combined with the underlying open-source code attribute, defines an attractive scenario
for sharing knowledge about lidar uncertainties estimation methods. It also encourages
collaborations among lidar field experts aiming to characterize a common lidar architecture
for different types of lidars, to assess lidar data processing methods or even helps to get
a consensus for lidar terminology, giving place to a lidar ontology, which is a developing
project driven by Andy Clifton, Nikola Vasiljevic and in collaboration with Francisco Costa [@OntoStack;@sheet2rdf]. 

The source code for ``Qlunc`` has been archived to Zenodo with the linked DOI: [@zenodo]

# Motivation

Measuring uncertainty means doubt about the validity of the result of a measurement [@GUM]
or, in other words, it represents the dispersion of the values attributed to a measurand.
The importance of knowing uncertainty in measurements lies both, on the quality of the
measurement as on the understanding of the results, and it can have a huge impact on
the veracity of an experiment or measuring set up. In this sense, wind lidar measurement
uncertainties assessment plays a crucial role, since it can determine decision-making
processes and therefore the global performance of a wind facility.

The scope of this project is to create an open, common and collaborative reference numerical
framework to describe unique lidar architectures, characterize lidar uncertainties and provide
a tool for others to contribute within those frameworks. This is so, but following lines of
OpenScience Principles, the underlying main motivation of this project is to create open and
sharable tools and knowledge, to reinforce or promote new or existing links and to foster
collaborations among research institutions and/or industry, within the wind energy community,
but not limited to it. 

# ``Qlunc`` available capabilities

Currently, ``Qlunc`` can perform both, VAD and scanning lidar patterns. For now, it can perform
lidar hardware uncertainties from photonics module, including photodetector (with or without
trans-impedance amplifier) and optical amplifier components, as well as optics module uncertainty
including scanner pointing accuracy distance errors and optical circulator uncertainties. In the
near future, uncertainties regarding other hardware components and data processing methods will
be impemented in the model.

Output plots show different signal noise contributors of the photodetector components and estimates
of scanning points distance uncertainty.

# Usage

## Creating a lidar digital twin

Each component, pertaining to the correspondent module (e.g. photodetector belongs to the photonics
module) is created as a python object and enclosed in other python class, which represents the aforementioned
module. Following this procedure these lidar modules are, in turn, included in the lidar python class, which
gathers all classes corresponding to the different modules a lidar is made of, thus creating the lidar
digital twin. Dot notation methodology is used to ask for lidar component properties.

!['Qlunc basic structure.'](Qlunc_BasicStructure_diagram.png)


## Uncertainty estimation model

All components are characterized by their technical parameters and their uncertainty functions,
which are feed to the code via a yaml file. Combined uncertainties throughout components and modules
are computed according to the Guide to the expression of Uncertainty in Measurement [@GUM] ([GUM](https://www.bipm.org/utils/common/documents/jcgm/JCGM_100_2008_E.pdf)) model. 

As mentioned above, the code claims flexibility and aims to foster collaboration, especially among researchers.
To encourage both, flexibility and further collaborations each lidar module has its own uncertainty estimation
function, which includes the components the module is made of. These stand-alone uncertainty estimation
functions are easily exchangeable, just in case users want to use another uncertainty model. 

# Working example and Tutorials: Do it yourself

Included in the Qlunc repository users can find Jupyter Notebooks-based tutorials
(https://github.com/SWE-UniStuttgart/Qlunc/tree/Qlunc-V0.9/Tutorials) on how Qlunc works, providing a tool
to help them get started with the software. Tutorials’ Binder badge is also provided to ease accessibility 
and reproducibility. Users can find more info about these tutorials in the readme file attached to the Qlunc repository.
Apart from the tutorials, the package includes a functional working example. More information about this
working example is given in the readme, included in the Qlunc repository, where the process of creating a
lidar digital twin is treated in depth.

# Future development roadmap

Over the next year, we plan to implement further lidar hardware modules in the model and compute their combined uncertainties.
Most significant data Processing methods, which are expected to be the highest uncertainty contributors, will be
assessed and implemented in the model during the next project stage, as well. 

``Qlunc`` is a modular numerical framework, aiming to combine with other lidar codes dealing with lidar uncertaintes. 
In this sense, ``Qlunc`` in combination with other existing tools like yaddum [@yaddum] and mocalum [@mocalum] will
help to improve lidar uncertainty estimations, thus increasing lidar measurements reliability. The "openness" of
these group of tools makes it possible to share within the wind energy community and even beyond it.

One of the next objectives is to align the lidar components/parameters/characteristics labeling process, used by Qlunc, to
the controlled vocabulary from an ongoing collaboration regarding a lidar ontology, aiming to achieve a standard for
lidar components labeling.

All documentation from the project, scientific articles derived from the research period, tutorials and raw code as well are meant
to be provided throughout a sphinx-based online site, to give possible users all needed information to dive into
the numerical framework and get used to the Qlunc routine.

# Acknowledgements

Author want also to thank Andrew Clifton, Nikola Vasiljevic and Ines Würth for their support and valuable suggestions,
feedback and insight.
This project has received funding from the European Union's Horizon 2020 research and innovation programme
under grant agreement No 858358, within the frame of LIKE project.

# References
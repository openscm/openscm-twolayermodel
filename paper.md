---
title: 'OpenSCM Two Layer Model: A Python implementation of the two-layer climate model'
tags:
  - Python
  - climate science
  - temperature projections
  - simple climate model
  - energy balance
  - reduced complexity climate model
authors:
  - name: Zebedee R. J. Nicholls
    orcid: 0000-0003-0872-7098
    affiliation: "1, 2"
  - name: Jared Lewis
    affiliation: 1
affiliations:
 - name: Australian-German Climate & Energy College, The University of Melbourne, Parkville, Victoria, Australia
   index: 1
 - name: School of Earth Sciences, The University of Melbourne, Parkville, Victoria, Australia
   index: 2
date: 7 October 2020
bibliography: paper.bib
---

# Summary

The evolution of the climate is controlled by highly complex physical dynamics.
However, simplified representations are surprisingly powerful tools for understanding these dynamics [@held_2010_two_layer] and making climate projections [@meinshausen_2011_rcp].
The field of simple climate modelling is widely used, in particular for assessing the climatic implications of large numbers of different emissions scenarios, a task which cannot be performed with more complex models because of computational constraints.

One of the most commonly used models of the climate's response to changes in the "Earth's energy balance" 
(energy input compared to energy output of the earth system) is the two-layer model originally introduced by @held_2010_two_layer.
While this model must be given energy imbalances (more precisely, radiative forcing) rather than emissions, it is nonetheless a widely used tool within climate science.
Approximately speaking, the model represents the Earth System as an ocean with two-layers.
The upper layer absorbs excess heat in the Earth System and then exchanges heat with the deep layer.
As a result, in response to a perturbation, the model responds with a distinctive two-timescale response, commonly referred to as the "fast" and "slow" warming components.
Since @held_2010_two_layer, the model has been extended to include updated representations of the efficiency of ocean heat uptake [@geoffroy_2013_two_layer2] as well as a state-dependent response to radiative forcing [@bloch_johnson_2015_feedback_dependence; @rohrschneider_2019_simple].

"OpenSCM Two Layer Model" is an object-oriented, open-source implementation of the two-layer model.
It provides an extensible interface for the two-layer model, which could then be coupled with other modules as researchers see fit.
The implementation also provides an easy way to convert between the two-layer model of @held_2010_two_layer and the mathematically equivalent two-timescale impulse response model, used most notably as the thermal core of the FaIR model [@smith_2018_fairv1_3].
The conversion between the two is an implementation of the proof by @geoffroy_2013_two_layer1.

# Statement of need

OpenSCM Two Layer Model was designed to provide a clean, modularised, extensible interface for one of the most commonly used simple climate models.
It was used in Phase 1 of the Reduced Complexity Model Intercomparison Project [@rcmip_phase_1] as a point of comparison for the other participating models.

The FaIR model [@fair_repo] implements a mathematically equivalent model but does not provide as clear a conversion between the two-layer model and the two-timescale response as is provided here.
We hope that this implementation could interface with other simple climate models like FaIR to allow simpler exploration of the combined behaviour of interacting climate components with minimal coupling headaches.

As implemented here, the "OpenSCM Two Layer Model" interface is intended to be used in research or education.

# Acknowledgements

We thank Robert Gieseke for comments on the manuscript and for all of his efforts within the OpenSCM project.

# References

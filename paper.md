---
title: 'OpenSCM Two Layer Model: A Python implementation of the two-layer climate model'
tags:
  - Python
  - climate science
  - temperature projections
  - simple models
authors:
  - name: Zebedee R. J. Nicholls
    orcid: 0000-0003-0872-7098
    affiliation: "1, 2" # (Multiple affiliations must be quoted)
  - name: Robert Gieseke
    affiliation: 3
  - name: Jared Lewis
    affiliation: 1
affiliations:
 - name: Australian-German Climate & Energy College, The University of Melbourne, Parkville, Victoria, Australia
   index: 1
 - name: School of Earth Sciences, The University of Melbourne, Parkville, Victoria, Australia
   index: 2
 - name: Institution 3
   index: 3
date: 15 May 2020
bibliography: paper.bib
---

# Summary

The evolution of the climate is controlled by highly complex physical dynamics.
However, simplified representations are surprisingly powerful tools for understanding these dynamics [@held_2010_two_layer] and making climate projections [@meinshausen_2011_rcp].
The field of simple climate modelling is widely used, in particular for assessing the climatic implications of large numbers of different emissions scenarios, a task which cannot be performed with more complex models because of computational constraints.

One of the most commonly used models of the climate's response to changes in the `Earth's energy balance' (energy in compared to energy out of the earth system) is the two-layer model originally introduced by @held_2010_two_layer.
While this model must be given energy imbalances (more precisely, radiative forcing) rather than emissions, it is nonetheless a widely used tool within climate science.
Since @held_2010_two_layer, the model has been extended to include updated representations of the efficiency of ocean heat uptake [@geoffroy_2013_two_layer2] as well as a state-dependent response to radiative forcing [@bloch_johnson_2015_feedback_dependence; @rohrschneider_2019_simple].

`OpenSCM Two Layer Model' is an object-oriented, open-source implementation of the two-layer model.
It provides an extensible interface for the two-layer model, which could then be coupled with other modules as researchers see fit.
The implementation also provides an easy way to convert between the two-layer model of @held_2010_two_layer and the mathematically equivalent two-timescale impulse response model, used most notably as the thermal core of the FaIR model [@smith_2018_fairv1_3].
The conversion between the two is an implementation of the proof by @geoffroy_2013_two_layer1.


- needed as much easier to plug bits and pieces into, easier to extend, useful conversion between two forms which is not currently available
- upgrades FaIR implementation to be modulare and object-oriented


# References

# Space Weather Risks to Satellites

Computational research investigating the relationship between space weather
and satellite risk in Low Earth Orbit (LEO).

This project combines satellite orbital data with geomagnetic and solar
activity measurements to study how elevated space-weather conditions may
affect satellite operations and orbital decay.

## Research Overview

The project examines several indicators of space-weather activity, including:

- Geomagnetic activity measured by the Kp index
- Solar X-ray flux from GOES observations
- Coronal mass ejection (CME) properties
- Historical orbital data for selected satellites

The current analysis focuses on determining whether periods of elevated
geomagnetic activity are associated with increased satellite orbital decay.

## Current Analysis

Historical orbital elements are used to calculate approximate satellite
altitudes from mean motion using Kepler's third law. Daily altitude changes
are then compared with geomagnetic activity to examine differences between
storm and quiet periods.

## Data Sources

- Space-Track satellite orbital data
- GFZ Potsdam Kp index
- NASA DONKI CME data
- GOES X-ray measurements

## Repository Structure

- `src/` — Python analysis and data-processing code
- `notebooks/` — research notebooks analysis
- `data/` — processed datasets and instructions for obtaining raw data
- `figures/` — figures generated from the analysis
- `docs/` — research posters and supporting documentation

## Status

Ongoing undergraduate research project.

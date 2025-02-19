# Machine vision application in workpiece dimensional control

Software solution was developed as a part of the automated measurement system. System is explained in detail in master's thesis [Machine vision application in workpieces dimensional control](thesis/Masters_thesis_Tomislav_Bazina_Full.pdf).

## Summary

In the first section of the thesis, an automated visual inspection system for O-ring measurement is proposed. Measured O-ring features are also defined. Optical system components, calibration and setup are described. Measurement system software solution, developed using the Python programming language and the open-source software, is also introduced. Instructions for using software solution graphical interface are composed, and the algorithms for calibration, measurement and digital image preprocessing are defined.

The second part of thesis presents methods for measuring the O-ring using micrometer and the optical measurement system. The capability of each system is analyzed using the Six Sigma methodology. Optical measurement system sensitivity to the calibration is examined. Automated and manual measurement systems were compared by means of repeatability and reproducibility and intraclass correlation coefficient. Finally, the measures to increase the quality of the optical measurement system are proposed.

## Getting started

1. Install Python 3.6+ and all [Prerequisites](#prerequisites)
1. Connect Basler USB 3.0 Camera for image grabbing (exactly this type of camera is necessary for parameter control using *pypylon*)
1. Run script `main.py`

### Content

Structure:
* Package cam:
  * `cam.py`
    * Object for interaction with camera, setting parameters and grabbing images
  * `event_handlers.py`
    * Camera event handlers
* Package gui:
  * `flowcharts.py`
    * PyQtGraph Flowchart windows and libraries
  * `mainwindow.py`
    * Application Main window and functions
  * `ptrees.py`
    * Parameter trees shown in Main window
  * `visualize.py`
    * Windows for grabbed frames, image preparation, dip.Image and real-time measurement
* Package processing:
  * `nodes.py`
    * Nodes as main processing blocks in flowcharts
  * `process.py`
    * Objects for parallel processing
* `main.py`
  * Launching application
* `calibrate_flowchart.fc`
  * Stored calibration flowchart
* `measure_flowchart.fc`
  * Stored measurement flowchart
* `measurement_result.tsv`
  * Stored measurement result
* Folder measurement_result
  * Stored measurement results

### Prerequisites

Drivers:
* [pylon 5.2.0 Camera Software Suite](https://www.baslerweb.com/en/sales-support/downloads/software-downloads/pylon-5-2-0-linux-x86-64-bit-debian/)

Python modules:
* [NumPy](https://github.com/numpy/numpy)
* [SciPy](https://github.com/scipy/scipy)
* [pypylon](https://github.com/basler/pypylon)
* [DIPlib 3 with PyDIP 3](https://github.com/DIPlib/diplib)
* [PyQtGraph](https://github.com/pyqtgraph/pyqtgraph)
  * **Note**: PyQtGraph might need some slight modifications to work proprely with Python 3.6
* [multiprocess](https://github.com/uqfoundation/multiprocess)

### Video example

Example usage:

<video width="800" height="480" controls preload>
  <source src="https://raw.githubusercontent.com/tbazina/dimension-visual-inspection/master/docs/video/measurement_procedure_reencode.mp4"></source>
  <source src="https://raw.githubusercontent.com/tbazina/dimension-visual-inspection/master/docs/video/measurement_procedure_reencode.webm"></source>
</video>

## Measurement system analysis

Simple R script `measurement_system_analysis.R` for optical system capability analysis is located in folder measurement_analysis. Folder also contains input data in .csv format and output images.

### R Libraries

Following R libraries are required to run script:
* [readr](https://github.com/tidyverse/readr)
* [qualityTools](http://www.r-qualitytools.org/)
* [SixSigma](http://www.sixsigmawithr.com/)
* [irr](https://cran.r-project.org/web/packages/irr/index.html)
* [ggplot2](https://github.com/tidyverse/ggplot2)
* [Hmisc](http://biostat.mc.vanderbilt.edu/wiki/Main/Hmisc)
* [dplyr](https://github.com/tidyverse/dplyr)
* [tidyr](https://github.com/tidyverse/tidyr)

## License

This project is licensed under the BSD 3-Clause License - see the [LICENSE.md](https://raw.githubusercontent.com/tbazina/dimension-visual-inspection/master/LICENSE.md) file for details

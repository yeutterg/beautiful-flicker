# Beautiful Flicker

A set of Python tools to compute and display lighting flicker data.

For example, it can plot a flicker waveform and display automatically-computed flicker metrics:

![Flicker Waveform](/out/example_0.png)

It can plot the flicker frequency and percentage on an IEEE PAR 1789-2015 flicker graphic:

![IEEE 1789 Flicker Graphic](/out/Low%20Blue%20Flicker%20Comparison.png)

This tool can be scripted for use in automated test scenarios. For custom versions of this software and testing services, please [get in touch](mailto:gregyeutter@gmail.com?subject=Beautiful%20Flicker%20Inquiry).

**Disclaimer:** This tool is an early alpha version! Things may not work, and breaking changes may occur between versions. Please open a new issue or submit a pull request if you encounter any problems. Please open a new issue for feature requests.

**See also:** [Beautiful Photometry](https://github.com/yeutterg/beautiful-photometry)

## Install and Use

### Local Version

Make sure you have Python installed in your environment. This only works with Python 3.5+.

Clone this repository, cd to the downloaded directory, and install necessary dependencies:

```console
pip install -r src/requirements.txt
```

To use Jupyter Notebooks, run from the root of this project:

```console
jupyter notebook examples/
```

### Docker Version

Alternatively, you can run this project in Docker. This is more likely to work across different systems.

Instructions for Docker are provided in [DOCKER.md](DOCKER.md)

### Examples

Examples of how to use this project can be found in the [examples](/examples/) folder:

* [Example 0: Importing and Plotting Waveforms](/examples/Example%200%20-%20Importing%20and%20Plotting%20Waveforms.ipynb)
* **More to come!**


### Documentation

In addition to the heavily-documented [codebase](/src/), an HTML version of the documentation is available. Access it by cloning the repository and opening this location in your browser:

```
/docs/build/html/index.html 
```

## Selected Flicker Resources

* IEEE 1789-2015 [Standard](http://www.bio-licht.org/02_resources/info_ieee_2015_standards-1789.pdf) and [Presentation](https://www.energy.gov/sites/prod/files/2015/05/f22/miller%2Blehman_flicker_lightfair2015.pdf) (PDFs)
* WELL Building Standard [L07 P2](https://v2.wellcertified.com/v/en/light/feature/7)
* California 2019 [JA8](https://efiling.energy.ca.gov/GetDocument.aspx?tn=223245-9&DocumentContentId=27701) and [JA10](https://efiling.energy.ca.gov/GetDocument.aspx?tn=223245-11&DocumentContentId=27684) (PDFs)
* [Photodiode Circuits](http://budgetlightforum.com/node/61254) (We use the OSRAM BPW34)

## License

Distributed under the [MIT license](/LICENSE).
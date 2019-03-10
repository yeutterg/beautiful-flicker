# Beautiful Flicker

A set of tools to compute and display lighting flicker data.

For example, it can plot a flicker waveform and display automatically-computed flicker metrics:

![Flicker Waveform](/out/fullheight.png)

It can plot the flicker frequency and percentage on an [IEEE PAR 1789-2015][1789-2015] flicker graphic:

![IEEE 1789 Flicker Graphic](/out/Low%20Blue%20Flicker%20Comparison.png)

**Disclaimer:** This tool is an early alpha version! Things may not work, and breaking changes may occur between versions. Please open a new issue or submit a pull request if you encounter any problems. Please open a new issue for feature requests.

**See also:** [Beautiful Photometry](https://github.com/yeutterg/beautiful-photometry)

## [Install]

Make sure you have Python installed in your environment. This only works with Python 3+.

Clone this repository, cd to the downloaded directory, and install necessary dependencies:

```
pip install -r src/requirements.txt
```

## Use

### Examples

Examples of how to use this project can be found in the [examples](/examples/) folder.

To run and modify the Jupyter Notebooks, or to create a new one: 

1. Follow the [installation instructions](#install)

2. Run from the root of this project:

    ```
    jupyter notebook examples/
    ```

### Documentation

In addition to the heavily-documented [codebase](/src/), an [HTML version](/docs/build/html/index.html) of the documentation is available. 

## Selected Flicker Resources

* IEEE [1789-2015](https://www.energy.gov/sites/prod/files/2015/05/f22/miller%2Blehman_flicker_lightfair2015.pdf) (PDF)
* WELL Building Standard [L07 P2](https://v2.wellcertified.com/v/en/light/feature/7)
* California 2019 [JA8]() and [JA10](https://efiling.energy.ca.gov/GetDocument.aspx?tn=223245-11&DocumentContentId=27684) (PDFs)

## License

Distributed under the [MIT license](/LICENSE).
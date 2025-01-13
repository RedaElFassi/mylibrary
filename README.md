# mylibrary

package for the python project 2025 class

## Installation

```bash
$ pip install mylibrary
```

## Usage

- TODO

## Overview and explanation of the package/code

In this project, i import pybacktestchain, which is a package developped by our professor, i then use the output given from his backtest function, which is in a blockchain format, i transform it into a dataframe in order to be able to analyse the data and further develop some functions for statistical analysis. The goal of this project is to develop a dashboard that will first display some key indicators for portfolio analysis so i use the portfolio obtained from the backtest function, i then plot the performance of the portfolio and the performance of the stocks contained in the portfolio (by this i mean their return). Once this is done, i add a table to display the sharpes ratios. I further contribute by developping some functions that will import the data from yahoo finance of the stocks considered in the first drown-down list on the dashboard, and allows to analyse them and display some statistical indicators and technical analysis (moving averages with different windows, bollinger bands) individually on a graph for each stocks.

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`mylibrary` was created by Reda El Fassi. It is licensed under the terms of the MIT license.

## Credits

`mylibrary` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).

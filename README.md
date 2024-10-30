# pywebcoos

A Python wrapper for the WebCOOS API.


## Table of Contents
- [Installation](#installation)
- [Test](#test)
- [Usage](#usage)
- [Disclaimer](#disclaimer)
- [License](#license)
- [Contact](#contact)


## Installation

For general use:

```bash
pip install git+https://github.com/WebCOOS/py-webcoos-client.git#egg=pywebcoos
```

For development:

```bash
git clone https://github.com/WebCOOS/py-webcoos-client.git
cd py-webcoos-client
conda env create -f environment.yml
conda activate py-webcoos-client
```


## Test

Unit and integration tests are included. 

To run the tests, follow the "For development" installation instructions. Then, set your WebCOOS API key as an environmental variable:

Linux:
```bash
export API_KEY='your_key'
```

Windows:
```bash
setx API_KEY 'your_key'
```

Then you can run the tests with:

```bash
pytest -v
```

## Usage

```python
import pywebcoos
api = pywebcoos.API('your_API_token')
print(api.get_cameras())
print(api.get_products('Charleston Harbor, SC'))
print(api.get_inventory('Charleston Harbor, SC','video-archive'))
files = api.download('Charleston Harbor, SC','video-archive','202401011000','202401011030',interval=1,save_dir='.')
```

See demo.ipynb for more usage details.


## Disclaimer
#### NOAA Open Source Disclaimer:

This repository is a scientific product and is not official communication of the National Oceanic and Atmospheric Administration, or the United States Department of Commerce. All NOAA GitHub project code is provided on an ?as is? basis and the user assumes responsibility for its use. Any claims against the Department of Commerce or Department of Commerce bureaus stemming from the use of this GitHub project will be governed by all applicable Federal law. Any reference to specific commercial products, processes, or services by service mark, trademark, manufacturer, or otherwise, does not constitute or imply their endorsement, recommendation or favoring by the Department of Commerce. The Department of Commerce seal and logo, or the seal and logo of a DOC bureau, shall not be used in any manner to imply endorsement of any commercial product or activity by DOC or the United States Government.


## License

Software code created by U.S. Government employees is not subject to copyright in the United States (17 U.S.C. �105). The United States/Department of Commerce reserve all rights to seek and obtain copyright protection in countries other than the United States for Software authored in its entirety by the Department of Commerce. To this end, the Department of Commerce hereby grants to Recipient a royalty-free, nonexclusive license to use, copy, and create derivative works of the Software outside of the United States.


## Contact

Package written by:

Greg Dusek\
NOAA Center for Operational Oceanographic Products and Services\
gregory.dusek@noaa.gov

Matthew P. Conlin\
Ocean Associates, Inc. in support of NOAA CO-OPS\
matthew.conlin@noaa.gov


For additional information, contact:

Greg Dusek\
NOAA Center for Operational Oceanographic Products and Services\
gregory.dusek@noaa.gov








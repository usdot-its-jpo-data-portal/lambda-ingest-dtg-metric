# Summary

This repository contains a lambda function for ingesting usage metrics relating to ITS DataHub's assets on data.transportation.gov. The metrics are ingested into ITS DataHub's Elasticsearch database for display on ITS DataHub.

# README Outline:
* Project Description
* Prerequisites
* Usage
	* Building
	* Testing
	* Execution
* Version History and Retention
* License
* Contributions
* Contact Information
* Acknowledgements

# Project Description

This repository contains a lambda function for ingesting usage metrics relating to ITS DataHub's assets on data.transportation.gov and datahub.transportation.gov. The metrics are ingested into ITS DataHub's Elasticsearch database for display on ITS DataHub.

For more information on the Socrata metrics, please see Socrata's support articles for [Socrata Site Analytics](https://support.socrata.com/hc/en-us/articles/360045612793-Socrata-Site-Analytics) and [Site Analytics: Asset Access](https://support.socrata.com/hc/en-us/articles/360051223314).

# Prerequisites

Requires:
- Python 3.6+
- Elasticsearch (optional if you choose to write metrics to CSV)

# Usage

## Building and Deploying
 
Option 1: Build package locally and deploy to lambda manually through AWS console.
```
sh package.sh
```

Option 2: Install requirements in local virtual environment for running as a script locally.
```
virtualenv --python=python3 temp_env/
source temp_env/bin/activate
pip install -r requirements.txt
```

For both options, make sure to set the following environment variables:

- `SOCRATA_COMMA_DELIM_AUTH`: Required. Socrata username followed by Socrata password, comma delimited. Example: `someUsername,somePassword`
- `ELASTICSEARCH_API_BASE_URL`: Required if writing to Elasticsearch. The Base URL to your Elasticsearch instance. Example: `https://my.elasticsearch-db.com`

If running locally, you can run the following command to set environment variable:

```
export SOCRATA_COMMA_DELIM_AUTH=someUsername,somePassword
export ELASTICSEARCH_API_BASE_URL=https://my.elasticsearch-db.com
```

## Execution

Option 1: Execute via AWS Lambda

Option 2: Execute locally as a script.
```
python src/lambda_function.py --help

usage: lambda_function.py [-h] [--ingest_historical] [--write_to_es] [--es_host ES_HOST]

optional arguments:
  -h, --help           show this help message and exit
  --ingest_historical  Ingest all daily DTG metrics from 2017-11-01 until yesterday. Otherwise, will ingest only metrics for yesterday.
  --write_to_es        Write metrics Elasticsearch. Otherwise, will write metrics to CSV.
  --es_host ES_HOST    Elasticsearch host to write the metrics to. Default: http://localhost.
```

# Version History and Retention

**Status:** This project is in the prototype phase.

**Release Frequency:** This project is currently in development and updated weekly.

**Release History: See [CHANGELOG.md](CHANGELOG.md)**

**Retention:** This project will remain publicly accessible for a minimum of five years (until at least 06/15/2025).

# License

This project is licensed under the Creative Commons 1.0 Universal (CC0 1.0) License - see the [LICENSE](https://github.com/usdot-jpo-codehub/codehub-readme-template/blob/master/LICENSE) for more details. 

# Contributions
Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our Code of Conduct, the process for submitting pull requests to us, and how contributions will be released.

# Contact Information

Contact Name: ITS JPO
Contact Information: data.itsjpo@dot.gov

# Acknowledgements

## Citing this code

When you copy or adapt from this code, please include the original URL you copied the source code from and date of retrieval as a comment in your code. Additional information on how to cite can be found in the [ITS CodeHub FAQ](https://its.dot.gov/code/#/faqs).

## Contributors
Shout out to [PurpleBooth](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2) for their README template.

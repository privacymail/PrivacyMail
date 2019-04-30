# PrivacyMail

Privacy as an eMail privacy analysis system. For more information about the platform, visit [privacymail.info](https://privacymail.info).

## Installation
PrivacyMail is a Django-based website. The `ansible` folder contains a deployment script that uses [Ansible](https://www.ansible.com/). See the README in that folder for additional details on what you need to set up to allow the system to deploy correctly. There are also some additional manual steps involved in setting up the necessary cronjobs to automate the retrieval and analysis of eMails. These steps are also described in the README file.

## Development
If you want to do some local development, you will need to set up your own `privacymail/privacymail/settings.py`. See `ansible/templates/settings.py` for the template. Make sure to replace all statements that look like `{{ lookup( [...] ) }}`, as these are directives that are interpreted by Ansible during the deployment process.

As a minimum, you will need to set up a virtualenv, install the dependencies from the `requirements.txt` file, set up the settings file as mentioned above, and provide the system with a Postgres database (docker works fine here). Afterwards, run the database migrations, and you should be good to go. However, in this setup, you will be unable to analyze eMails. For this, you will also need to set up [OpenWPM](https://github.com/mozilla/openwpm) (included as a submodule in this git repository) and configure eMail servers in settings.py. For details on the OpenWPM setup, check the ansible deployment playbook.

## License
PrivacyMail is licensed under the GPLv3 license.

## Citation
If you use PrivacyMail in a scientific project, please cite our paper at the Annual Privacy Forum 2019:

```
@article{PrivacyMail,
	title = {{Towards Transparency in Email Tracking}},
	author = {Maass, Max and Schwär, Stephan and Hollick, Matthias},
	journal = {Annual Privacy Forum},
	year = {2019}
}
```

## Acknowledgement
The creation of PrivacyMail was funded in part by the DFG as part of project C.1 within the [RTG 2050 "Privacy and Trust for Mobile Users"](https://www.informatik.tu-darmstadt.de/privacy-trust/privacy_and_trust/index.en.jsp).
source /opt/conda/etc/profile.d/conda.sh
conda activate privacymail

cd /opt/privacymail/privacymail

python manage.py runcrons

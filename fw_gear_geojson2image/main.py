"""Main module."""
import logging
import os
import json
import shutil
from zipfile import ZipFile

from fw_core_client import CoreClient
from flywheel_gear_toolkit import GearToolkitContext
import flywheel

from .make_polygon_image import create_labeled_image

from .run_level import get_analysis_run_level_and_hierarchy
# from .get_analysis import get_matching_analysis

log = logging.getLogger(__name__)

fw_context = flywheel.GearContext()
fw = fw_context.client

def run(client: CoreClient, gtk_context: GearToolkitContext):
    """Main entrypoint

    Args:
        client (CoreClient): Client to connect to API
        gtk_context (GearToolkitContext)
    """
    # get the Flywheel hierarchy for the run
    destination_id = gtk_context.destination["id"]
    hierarchy = get_analysis_run_level_and_hierarchy(gtk_context.client, destination_id)
    acq_label = hierarchy['acquisition_label']
    sub_label = hierarchy['subject_label']
    ses_label = hierarchy['session_label']
    project_label = hierarchy['project_label']
    group_name = hierarchy['group']

    # get the output acqusition container
    acq = fw.lookup(f'{group_name}/{project_label}/{sub_label}/{ses_label}/{acq_label}')
    acq = acq.reload()

    # get the input file
    CONFIG_FILE_PATH = '/flywheel/v0/config.json'
    with open(CONFIG_FILE_PATH) as config_file:
        config = json.load(config_file)

    input_file_name = config['inputs']['input_file']['location']['path']

    # run the main processes & upload output file back to acquisition
    print(f'Processing GeoJSON file: {input_file_name}')
    base_fn   = input_file_name.split('.geojson')[0] # full path minus the file ending
    output_fn = f'{base_fn}_labeled_mask.png' # add desired file ending to full path
    create_labeled_image(input_file_name, output_fn)

    print(f'Uploading to {acq.label} acquisition: {output_fn}')
    acq.upload_file(f'{output_fn}')
    os.remove(f'{output_fn}') # remove from instance to save space
